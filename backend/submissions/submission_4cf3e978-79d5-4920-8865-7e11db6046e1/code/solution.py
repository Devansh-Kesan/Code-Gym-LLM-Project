def sum_of_list(lst):
    # Your code here
    sum(lst)

if __name__ == "__main__":
    nums = list(map(int, input().split()))
    print(sum_of_list(nums))