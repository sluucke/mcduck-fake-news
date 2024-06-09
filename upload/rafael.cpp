#include <iostream>
#include <algorithm>
#include <vector>
#include <map>
#include <queue>
#define MAX 205000
using ll = long long;
typedef std::pair<int,int> pii;
std::map<pii,std::vector<pii>> conexoes;
std::map<int,bool> tipos[MAX];
typedef std::pair<ll,pii> pli;
bool passa[MAX];
ll price[MAX];
std::map<pii,bool> passou;
int main()
{
        int N, M, K;
        std::cin>>N>>M>>K;
        for(int i=0;i!=K;++i){
            std::cin>>price[i];
        }
        for(int i=0;i!=M;++i){
            int a,b,c=0,d;
            std::cin>>a>>b>>d;--a;--b;
            conexoes[{a,d}].push_back({b,c});
            conexoes[{b,d}].push_back({a,c});
            tipos[a][d]=tipos[b][d]=1;
        }
        int A,B;
        std::cin>>A>>B;--A;--B;
        std::priority_queue<pli,std::vector<pli>,std::greater<pli>> queue;
        queue.push({0,{A,0}});
        while(queue.size()){
            auto __ = queue.top();
            queue.pop();
            ll custo = __.first;
            int pos = __.second.first;
            int chave = __.second.second;
            if(pos==B){///Chegou no final
                std::cout<<custo<<"\n";
                goto prox;
            }
            if(passou[__.second])continue;///Total MlogM
            passou[__.second]=1;
            if(!passa[pos]){///Simula troca de chave. Executa apenas no primeiro (menor) cara
                passa[pos]=1;
                for(auto&x:tipos[pos]){
                    ll c2 = price[x.first-1];
                    queue.push({custo+c2,{pos,x.first}});
                }
            }
            for(auto&x:conexoes[__.second]){///Anda para todos os caras da mesma cor
                queue.push({custo+(ll)x.second,{x.first,chave}});
            }
        }
        ///Impossivel alcancar o final
        std::cout<<"-1\n";
        prox:{}
}
