from pathlib import Path
import joblib


MODEL_DIR = Path("app/modules/lifestyle/models")


for model_path in MODEL_DIR.glob("*.pkl"):
    print("\n" + "=" * 70)
    print("MODEL:", model_path.name)
    print("=" * 70)

    try:
        model = joblib.load(model_path)

        print("Model type:", type(model))

        if hasattr(model, "feature_names_in_"):
            print("\nFeatures:")
            for feature in model.feature_names_in_:
                print("  -", feature)
        else:
            print("\nFeatures: Not directly available")

        if hasattr(model, "classes_"):
            print("Classes:", model.classes_)

        if hasattr(model, "steps"):
            print("\nPipeline steps:")
            for name, step in model.steps:
                print("  -", name, ":", type(step))

        if hasattr(model, "named_steps"):
            print("\nNamed steps:")
            for name, step in model.named_steps.items():
                print("  -", name, ":", type(step))

    except Exception as e:
        print("ERROR:", repr(e))