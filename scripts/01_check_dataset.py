from src.io import load_dataset

test_data, retest_data, subject_ids = load_dataset()

print(f"Subjects: {len(subject_ids)}")

print("Test shape:", test_data.shape)
print("Retest shape:", retest_data.shape)

print()

print("First subject:", subject_ids[0])

print("First five values:")
print(test_data[0, :5])