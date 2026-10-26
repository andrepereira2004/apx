#include <security/pam_modules.h>
#include <cstring>
#include <security/pam_ext.h>
extern "C" int pam_sm_authenticate(pam_handle_t* handle,int,int,const char**) {
 const char* token=nullptr; int result=pam_get_authtok(handle,PAM_AUTHTOK,&token,nullptr);
 return result==PAM_SUCCESS && token && std::strcmp(static_cast<const char*>(token),"fixture-accepted")==0?PAM_SUCCESS:PAM_AUTH_ERR;
}
extern "C" int pam_sm_setcred(pam_handle_t*,int,int,const char**) { return PAM_SUCCESS; }
