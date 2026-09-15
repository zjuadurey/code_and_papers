#include "gate_kernels.h"
// Appended virtual bit v is the high address bit. Generic U qargs=[v,p_target].
void transform(const Complex* x0,const Complex* x1,Complex* y0,Complex* y1,uint64_t count,int target,
               const std::string& gate,const Matrix& u){
    uint64_t mask=1ULL<<target;
    for(uint64_t i=0;i<count;++i){bool bit=i&mask;
        if(gate=="cx_product_control"){y0[i]=x0[i];y1[i]=x1[i^mask];}
        else if(gate=="cx_product_target"){y0[i]=bit?x1[i]:x0[i];y1[i]=bit?x0[i]:x1[i];}
        else if(gate=="cz"){y0[i]=x0[i];y1[i]=bit?-x1[i]:x1[i];}
        else{Complex a=0.,b=0.;for(int p=0;p<2;++p){uint64_t j=(i&~mask)|(p?mask:0);
            a+=u[(2*bit)*4+2*p]*x0[j]+u[(2*bit)*4+2*p+1]*x1[j];
            b+=u[(2*bit+1)*4+2*p]*x0[j]+u[(2*bit+1)*4+2*p+1]*x1[j];}y0[i]=a;y1[i]=b;}
    }
}
void fused(const Complex* x,Complex* y0,Complex* y1,uint64_t count,int target,
           Complex alpha,Complex beta,const std::string& gate,const Matrix& u){
    uint64_t mask=1ULL<<target;
    for(uint64_t i=0;i<count;++i){bool bit=i&mask;
        if(gate=="cx_product_control"){y0[i]=alpha*x[i];y1[i]=beta*x[i^mask];}
        else if(gate=="cx_product_target"){y0[i]=(bit?beta:alpha)*x[i];y1[i]=(bit?alpha:beta)*x[i];}
        else if(gate=="cz"){y0[i]=alpha*x[i];y1[i]=(bit?-beta:beta)*x[i];}
        else{Complex a=0.,b=0.;for(int p=0;p<2;++p){uint64_t j=(i&~mask)|(p?mask:0);
            a+=(u[(2*bit)*4+2*p]*alpha+u[(2*bit)*4+2*p+1]*beta)*x[j];
            b+=(u[(2*bit+1)*4+2*p]*alpha+u[(2*bit+1)*4+2*p+1]*beta)*x[j];}y0[i]=a;y1[i]=b;}
    }
}
