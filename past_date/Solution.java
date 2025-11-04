import java.lang.reflect.Array;
import java.util.Arrays;

class Solution {
    public int countDays(int days, int[][] meetings) {
        // sort meetings by the start time
        // meetings = Arrays.stream(meetings).sorted((a, b) -> Integer.compare(a[0], b[0])).toArray(int[][]::new);
        Arrays.sort(meetings, (a, b) -> Integer.compare(a[0], b[0]));
        int free_days = 0;
        
        // print the sorted meetings
        for(int i = 0; i < meetings.length; i++) {
            System.out.println("a: " + meetings[i][0] + " b: " + meetings[i][1]);
        }

        for(int i = 0; i < meetings.length; i++) {
            int a = meetings[i][0];
            int b = meetings[i][1];
            while(i + 1 < meetings.length){
                if (meetings[i + 1][0] <= b) {
                    System.out.println("1");
                    b = meetings[i + 1][1];
                    i++;
                }else if(a == meetings[i + 1][0] && meetings[i + 1][1] > meetings[i][1]) {
                    b = meetings[i + 1][1];
                    i++;
                }else if(a == meetings[i + 1][0] && meetings[i + 1][1] < meetings[i][1]){
                    i++;
                }else if (meetings[i][1] > meetings[i + 1][0]) {
                    b = meetings[i + 1][1];
                    i++;
                }
            }
            
            free_days += (b-a) + 1;
            // System.out.println("a: " + a + " b: " + b + " free_days: " + free_days);
        }
        return days - free_days;
    }

    public static void main(String[] args) {
        Solution sol = new Solution();
        int days = 10;
        // {{5,7},{1,3},{9,10}}
        int[][] meetings = new int[][]{{3,4},{4,8},{2,5},{3,8}};
        System.out.println(sol.countDays(days, meetings));
    }
}