from pathlib import Path
import joblib


MODEL_DIR = Path("app/modules/lifestyle/models")

MODELS = [
    "ckd_risk_model.pkl",
    "hypertension_model.pkl",
    "stroke_risk_model.pkl",
]


for model_name in MODELS:

    print("\n" + "=" * 80)
    print("MODEL:", model_name)
    print("=" * 80)

    model_path = MODEL_DIR / model_name
    pipeline = joblib.load(model_path)

    print("\nPipeline steps:")
    for name, step in pipeline.named_steps.items():
        print(f"  - {name}: {type(step)}")

    # ---------------------------------------------------------
    # CKD has no preprocessing
    # ---------------------------------------------------------
    if "preprocessor" not in pipeline.named_steps:
        print("\nNo preprocessor found.")
        continue

    preprocessor = pipeline.named_steps["preprocessor"]

    print("\nPreprocessor:")
    print(preprocessor)

    print("\nTransformer details:")

    for name, transformer, columns in preprocessor.transformers_:

        print("\nTransformer:", name)
        print("Columns:", columns)

        # Check if transformer is a Pipeline
        if hasattr(transformer, "named_steps"):

            print("Nested pipeline steps:")

            for step_name, step in transformer.named_steps.items():

                print(f"  - {step_name}: {type(step)}")

                # Check OneHotEncoder
                if hasattr(step, "categories_"):

                    print("\n    Categories:")

                    for column, categories in zip(
                        columns,
                        step.categories_
                    ):
                        print(
                            f"      {column}: {list(categories)}"
                        )