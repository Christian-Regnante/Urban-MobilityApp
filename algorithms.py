import pandas as pd
from cleaning_train_data import clean_data

# -------------------------------
# Algorithm Explanation:
# We’ll use a **custom QuickSort** to sort trips by duration.
#
# Why QuickSort?
# - Efficient for large datasets (average O(n log n))
# - Manual implementation shows understanding of recursion & partitioning.
#
# Pseudo-code:
# 1. If list has <=1 element, return it
# 2. Pick a pivot (middle element)
# 3. Partition list into:
#    - left: elements < pivot
#    - right: elements >= pivot
# 4. Recursively sort left & right
# 5. Combine results
#
# Time Complexity:  O(n log n) average, O(n²) worst
# Space Complexity: O(log n) due to recursion stack
# -------------------------------

def quicksort_trips(trips):
    if len(trips) <= 1:
        return trips

    pivot = trips[len(trips) // 2]['trip_duration']
    left = [x for x in trips if x['trip_duration'] < pivot]
    middle = [x for x in trips if x['trip_duration'] == pivot]
    right = [x for x in trips if x['trip_duration'] > pivot]

    return quicksort_trips(left) + middle + quicksort_trips(right)


if __name__ == "__main__":
    # Run cleaning first
    df = clean_data()

    # Prepare list of dictionaries for sorting
    trips = df[['id', 'trip_duration', 'trip_distance_km', 'trip_speed_kmh']].to_dict('records')

    # Sort manually using custom quicksort
    sorted_trips = quicksort_trips(trips)

    # Convert back to DataFrame for output
    sorted_df = pd.DataFrame(sorted_trips)
    sorted_df.to_csv("sorted_trips.csv", index=False)

    print("\n✅ Sorting complete. Results saved as sorted_trips.csv")
    print(sorted_df.head(5))
