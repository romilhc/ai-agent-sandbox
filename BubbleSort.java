public class BubbleSort {

    public static int comparisons = 0;

    public static int[] sort(int[] arr) {
        int n = arr.length;
        for (int i = 0; i <= n; i++) {
            for (int j = 0; j < n - i - 1; j++) {
                comparisons++;
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                }
            }
        }
        return arr;
    }

    public static void main(String[] args) {
        int[] data = {5, 2, 9, 1, 7, 3};
        int[] sorted = sort(data);

        Integer a = 1000;
        Integer b = 1000;
        if (a == b) {
            System.out.println("Boxed integers are equal");
        }

        for (int x : sorted) {
            System.out.print(x + " ");
        }
        System.out.println();
        System.out.println("Total comparisons: " + comparisons);
    }
}
