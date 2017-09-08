#include <iostream>
#include <fstream>
#include <string>
#include <sstream>
#include <string.h>
#include <vector>
#include <time.h>
#include <stdlib.h>
#include <algorithm>
#include <ctime>

class standings{
public:
    std::string name;
    int win;
    int lose;
    int draw;
    double pct;

    standings(){
        this->win = 0;
        this->lose = 0;
        this->draw = 0;
        this->pct = 0.0;
    }

    bool operator <(const standings &s) const {
        return this->pct < s.pct;
    }
};

bool cmp(const standings &a, const standings &b){
    return a.pct > b.pct;
}

std::vector<std::string> schedules;

standings stand[10];
standings stand_init[10];

/*
struct results{
    std::string name;
    int count;
};
*/

class results{
public:
    std::string name;
    int count;

    results(){
        this->count = 0;
    }
};

bool cmp_r(const results &a, const results&b){
    return a.count > b.count;
};

results res[10];

void add_results( std::string a )
{
    for(int i = 0; i < 10; i++)
    {
        if( res[i].name.compare(a) == 0 )
        {
            res[i].count ++;
            break;
        }
    }
};

void stand_win( std::string a )
{
    for(int i = 0; i < 10; i++)
    {
        if( stand[i].name.compare(a) == 0 )
        {
            stand[i].win++;
            break;
        }
    }
}

void stand_lose( std::string a )
{
    for(int i = 0; i < 10; i++)
    {
        if( stand[i].name.compare(a) == 0 )
        {
            stand[i].lose++;
            break;
        }
    }
}

void read_stand(){
    int i = -1;
    std::ifstream infile("stand.txt");
    std::string line;
    while( std::getline(infile, line) )
    {
        std::istringstream iss(line);
        int a, b, c;
        iss >> a >> b >> c;

        if( i < 0 )
        {
            i++;
            continue;
        }
        stand_init[i].win = a;
        stand_init[i].lose = b;
        stand_init[i].draw = c;
        i++;
    }
    infile.close();

    stand_init[0].name = "ki";
    stand_init[1].name = "ds";
    stand_init[2].name = "nc";
    stand_init[3].name = "lo";
    stand_init[4].name = "nx";
    stand_init[5].name = "sk";
    stand_init[6].name = "lg";
    stand_init[7].name = "hh";
    stand_init[8].name = "ss";
    stand_init[9].name = "kt";

    stand[0].name = "ki";
    stand[1].name = "ds";
    stand[2].name = "nc";
    stand[3].name = "lo";
    stand[4].name = "nx";
    stand[5].name = "sk";
    stand[6].name = "lg";
    stand[7].name = "hh";
    stand[8].name = "ss";
    stand[9].name = "kt";

    res[0].name = "ki";
    res[1].name = "ds";
    res[2].name = "nc";
    res[3].name = "lo";
    res[4].name = "nx";
    res[5].name = "sk";
    res[6].name = "lg";
    res[7].name = "hh";
    res[8].name = "ss";
    res[9].name = "kt";

    /*
    res[0].count = 0;
    res[1].count = 0;
    res[2].count = 0;
    res[3].count = 0;
    res[4].count = 0;
    res[5].count = 0;
    res[6].count = 0;
    res[7].count = 0;
    res[8].count = 0;
    res[9].count = 0;
    */
};

void init_stand(){
    for(int i=0; i<10; i++)
    {
        stand[i].win = stand_init[i].win;
        stand[i].lose = stand_init[i].lose;
        stand[i].draw = stand_init[i].draw;
        stand[i].pct = 0.0;
    }
};

void read_schedule()
{
    std::ifstream infile("schedule.txt");
    std::string line;
    int i = 0;
    while( std::getline(infile, line) )
    {
        if( line.length() == 4 )
        {
            schedules.push_back( line );
        }
        else
        {
            continue;
        }
    }
    infile.close();
};

int main(){
    int N = 1000000;
    clock_t begin = std::clock();

    read_stand();
    read_schedule();
    srand((unsigned int)time(NULL));

    for( int i = 0; i < N; i++ )
    {
        init_stand();
        for( int j = 0; j < schedules.size(); j++ )
        {
            std::string a = schedules[j].substr(0, 2);
            std::string b = schedules[j].substr(2, 4);
            int s = rand() % 10;
            if( s < 5 )
            {
                stand_win(a);
                stand_lose(b);
            }
            else
            {
                stand_win(b);
                stand_lose(a);
            }
        }

        std::vector<standings> v;
        for( int j = 0; j < 10; j++ )
        {
            stand[j].pct = (double)stand[j].win / ((double)stand[j].win + (double)stand[j].lose);
            v.push_back(stand[j]);
        }

        sort(v.begin(), v.end(), cmp);

        int counted = 0;
        int k = 0;
        while( counted < 5 )
        {
            if( v[k].pct == v[k+1].pct )
            {
                int l = k+1;
                while( v[l].pct == v[l+1].pct )
                    l++;
                while( k <= l )
                {
                    add_results( v[k].name );
                    k++;
                    counted ++;
                }
            }
            else
            {
                add_results( v[k].name );
                k++;
                counted ++;
            }
        }
    }

    std::vector<results> v;
    for( int i = 0; i < 10; i++ )
        v.push_back(res[i]);

    sort(v.begin(), v.end(), cmp_r);
    /*
    for( int i = 0; i < 10; i ++ )
    {
        printf("%d. %s : %.1f%%\n", i+1, res[i].name.c_str(), (double)res[i].count/(double)N*100);
    }
    */
    for( int i = 0; i < 10; i ++ )
    {
        printf("%d. %s : %.1f%%\n", i+1, v[i].name.c_str(), (double)v[i].count/(double)N*100);
    }

    clock_t end = std::clock();

    double elapsed = double( end - begin ) / CLOCKS_PER_SEC;

    printf("%.1f seconds elapsed\n", elapsed);

    return 0;
}