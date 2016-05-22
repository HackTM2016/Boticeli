#include <iostream>
#include <fstream>
#include <vector>
#include <stack>
#include <queue>

using namespace std;

#define BigVal 0x3f3f3f3f
#define MAX_SIZE 10005

typedef vector <int>::iterator iit;

ifstream in("directions.txt");
ifstream out("directions.out");

int Graph[MAX_SIZE][MAX_SIZE];
int Nr_Intersections, LineProcentaj;
int LocalMinimum = BigVal, MaximumOutput = -BigVal;
int GreenTime[MAX_SIZE] , New_GreenTime[MAX_SIZE];
int greentimeIncrease[105];
int line_to_increase, line_to_decrease;

void SetIntersections(void)
{	
	int i , count = 1 ;

	Nr_Intersections = 4;
	New_GreenTime[1] = GreenTime[1] = 30;
	New_GreenTime[2] = GreenTime[2] = 25;
	New_GreenTime[3] = GreenTime[3] = 30;
	New_GreenTime[4] = GreenTime[4] = 25;

	for (i = 0; i <= 100; ++i)
		if (i >= 33 && i <= 66) {
			 greentimeIncrease[i] = 15;
		}
		else if (i >= 66)
			 greentimeIncrease[i] = 30;
		else 
			 greentimeIncrease[i] = 0;

}

int get_min(int a, int b)
{
	if (a > b)
		return b;
	else
		return a;
}

int get_max(int a, int b)
{
	if (a < b)
		return b;
	else
		return a;
}

void FindNewGreenTimes(void)
{
	int i, j;
	float dummy =(float) ( ((float) MaximumOutput / (float)LineProcentaj) * 100);
	//cout << dummy << " ";
	int value = (greentimeIncrease[(int)dummy] * GreenTime[line_to_increase]) / 100;
	//cout << GreenTime[line_to_increase] << " "  << value << "\n";
	New_GreenTime[line_to_increase] = GreenTime[line_to_increase] + value ;
    //cout << line_to_decrease;
	New_GreenTime[line_to_decrease] = GreenTime[line_to_decrease] - value;
}

int main( void )
{
	int i, j;
	SetIntersections();
	for (i = 1; i <= Nr_Intersections; ++i) {
		for (j = 1; j <= Nr_Intersections; ++j) {
			in >> Graph[i][j];
			if (MaximumOutput < Graph[i][j]) {
				MaximumOutput = Graph[i][j];
				line_to_increase = i;
			}
		}
	}

	//Find LocalMinimum
	for (i = 1; i <= Nr_Intersections; ++i) {
		int TestValue = 0;
		for (j = 1; j <= Nr_Intersections; ++j)
			TestValue += Graph[i][j];
		if (line_to_increase == i)
			LineProcentaj = TestValue;
		if (LocalMinimum > TestValue) {
			LocalMinimum = TestValue;
			line_to_decrease = i;
		}
	}
	LocalMinimum += 1;


	/*
		from line_to_increase i have to increase the time for the green light
			 line_to_decrease ....
	*/

	FindNewGreenTimes();

	for (i = 1; i <= Nr_Intersections; ++i)
		cout << New_GreenTime[i] << " ";
	in.close();
	out.close();
	return  0;
}