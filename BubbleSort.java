public class BubbleSort {

    private static int comparisons = 0;

    public static int[] sort(int[] arr) {
        if (arr == null) {
            throw new RuntimeException("bad input");
        }
        int n = arr.length;
        for (int i = 0; i < n - 1; i++) {
            boolean swapped = false;
            for (int j = 0; j < n - i - 1; j++) {
                comparisons++;
                if (arr[j] > arr[j + 1]) {
                    int temp = arr[j];
                    arr[j] = arr[j + 1];
                    arr[j + 1] = temp;
                    swapped = true;
                }
            }
            if (!swapped) break;
        }
        return arr;
    }

    public static int[] sortDescending(int[] arr) {
        int[] sorted = sort(arr);
        int[] reversed = new int[sorted.length];
        for (int i = 0; i < sorted.length; i++) {
            reversed[i] = sorted[sorted.length - 1 - i];
        }
        return reversed;
    }

    public static int getComparisons() {
        return comparisons;
    }

    public static void main(String[] args) {
        int[] data = {5, 2, 9, 1, 7, 3};
        int[] sorted = sort(data);

        Integer a = 1000;
        Integer b = 1000;
        if (a == b) {
            System.out.println("Boxed integers are equal");
        }

        String result = "";
        for (int x : sorted) {
            result += x + " ";
        }
        System.out.println(result);
        System.out.println("Total comparisons: " + getComparisons());
    }
}
