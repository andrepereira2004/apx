#include <security/pam_appl.h>
#include <condition_variable>
#include <mutex>
#include <thread>
#include <chrono>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <sys/wait.h>
#include <cerrno>
using namespace std::chrono_literals;
struct State { std::mutex mutex; std::condition_variable condition; bool ready=false; bool submitted=false; bool reject=false; };
int conversation(int count,const pam_message** messages,pam_response** responses,void* ptr) {
 auto& state=*static_cast<State*>(ptr);
 auto reply=static_cast<pam_response*>(calloc(count,sizeof(pam_response)));
 for(int i=0;i<count;i++) if(messages[i]->msg_style==PAM_PROMPT_ECHO_OFF) {
  std::unique_lock<std::mutex> lock(state.mutex); state.ready=true; state.condition.notify_all();
  state.condition.wait(lock,[&]{return state.submitted;});
  reply[i].resp=strdup(state.reject?"fixture-rejected":"fixture-accepted");
 }
 *responses=reply; return PAM_SUCCESS;
}
int main(int argc,char** argv) {
 State state; state.reject=std::string(argv[1])=="reject";
 pam_conv conv={conversation,&state}; pam_handle_t* handle=nullptr;
 if(pam_start("apx-parallel-test","apx",&conv,&handle)!=PAM_SUCCESS) return 2;
 std::thread input([&]{
  std::unique_lock<std::mutex> lock(state.mutex);
  if(!state.condition.wait_for(lock,3s,[&]{return state.ready;})) return;
  lock.unlock(); std::this_thread::sleep_for(std::string(argv[1])=="face"?500ms:150ms); lock.lock();
  state.submitted=true; state.condition.notify_all();
 });
 auto start=std::chrono::steady_clock::now(); int result=pam_authenticate(handle,0);
 auto duration=std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::steady_clock::now()-start).count();
 pam_end(handle,result); input.join();
 int status; bool reaped=waitpid(-1,&status,WNOHANG)==-1 && errno==ECHILD;
 bool expected=state.reject?result!=PAM_SUCCESS:result==PAM_SUCCESS;
 std::cout<<argv[1]<<" result="<<result<<" prompt="<<state.ready<<" elapsed_ms="<<duration<<" reaped="<<reaped<<std::endl;
 return expected && state.ready && reaped && duration<1000?0:1;
}
