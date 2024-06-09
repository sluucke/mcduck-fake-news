#include <stdio.h>
int main(){
    int a,b,c,i=0,z, v;
    scanf("%d",&a);
    while(a>0){
        scanf("%d",&b);
        v=0;
        while(b>0){
            scanf("%d",&c);
            i++;
            if(!v && i==c){v=i;}
            b--;
        }
        printf("%d\n", v);
        i=0;
        a--;
    }
    
    
    
    return 0;
}
