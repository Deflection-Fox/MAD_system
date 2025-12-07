"""
Script to save MMLU-Pro validation set locally
"""
from datasets import load_dataset
import os


def save_dataset_locally():
    """Save MMLU-Pro validation set to local directory"""

    # Configuration
    dataset_name = "TIGER-Lab/MMLU-Pro"
    split_to_save = "validation"  # Save validation set
    local_save_path = "data/mmlu_pro_validation"  # Local directory

    print("📥 Loading MMLU-Pro dataset from Hugging Face...")

    try:
        # Load dataset
        ds = load_dataset(dataset_name)

        if split_to_save not in ds:
            print(f"❌ Split '{split_to_save}' not found in dataset.")
            print(f"   Available splits: {list(ds.keys())}")
            return

        # Get validation set
        validation_set = ds[split_to_save]
        print(f"✅ Loaded validation set: {len(validation_set)} samples")

        # Create directory if it doesn't exist
        os.makedirs(local_save_path, exist_ok=True)

        # Save to local directory
        print(f"💾 Saving to: {local_save_path}")
        validation_set.save_to_disk(local_save_path)

        print("✅ Successfully saved validation set locally!")

        # Show some statistics
        print(f"\n📊 Dataset info:")
        print(f"   - Total samples: {len(validation_set)}")
        print(f"   - Features: {validation_set.features}")

        # Show first sample structure
        print(f"\n📝 First sample structure:")
        first_sample = validation_set[0]
        for key, value in first_sample.items():
            if key == 'options' and isinstance(value, list):
                print(f"   - {key}: List of {len(value)} options")
            elif isinstance(value, str) and len(value) > 50:
                print(f"   - {key}: {value[:50]}...")
            else:
                print(f"   - {key}: {value}")

        return local_save_path

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    save_dataset_locally()