#include <iostream>
#include <vector>
using namespace std;

    int merge(vector<int>data, int l, int mid, int r)
    {
        vector<int> tmp(r-l+1);
        int k = 0;
        int count = 0;
        int p1 = l;
        int p2 = mid+1;
        while(p1<=mid&&p2<=r)
        {
            count += (data[p1]>data[p2])?(mid-p1+1):0;
            tmp[k++] = (data[p1]<data[p2])?data[p1++]:data[p2++];
        }
        while(p1<=mid)
           tmp[k++] = data[p1++];
        while(p2<=r)
            tmp[k++] = data[p2++];
        for(int i = 0;i<tmp.size();i++)
            data[l+i] = tmp[i];
        return count;
    }

    int MergeSort(vector<int> data, int L, int R)
    {
        if(L<R)
        {
            int mid = L + ((R-L)>>1);
            return MergeSort(data, L, mid)+MergeSort(data, mid+1, R)+merge(data, L, mid, R);      
         }
         else
            return 0;
    }
    
    int InversePairs(vector<int> data) {
        if(data.size() == 0|| data.size()<2) return 0;
        return MergeSort(data, 0, data.size()-1);
    }
    

    int main()
    {   
        int a[8] = {1,2,3,4,5,6,7,0};
        vector<int> data;
        for(int i =0;i<8;i++)
            data.push_back(a[i]);
        cout<<data[0]<<endl;
        return 0;
    }   