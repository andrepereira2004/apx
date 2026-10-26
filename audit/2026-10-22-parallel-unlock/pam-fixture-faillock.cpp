#include <security/pam_modules.h>
#include <cstring>
extern "C" int pam_sm_authenticate(pam_handle_t*,int,int argc,const char** argv) {
 for(int i=0;i<argc;i++) if(std::strcmp(argv[i],"authfail")==0) return PAM_AUTH_ERR;
 return PAM_SUCCESS;
}
extern "C" int pam_sm_setcred(pam_handle_t*,int,int,const char**) { return PAM_SUCCESS; }
