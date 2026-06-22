import os
import sys

def patch_file(filepath, target_content, replacement_content):
    if not os.path.exists(filepath):
        print(f"Error: File {filepath} not found. Skipping patch.")
        return False
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if target_content in content:
        new_content = content.replace(target_content, replacement_content)
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write(new_content)
        print(f"Successfully patched {os.path.basename(filepath)}")
        return True
    elif replacement_content in content:
        print(f"File {os.path.basename(filepath)} already patched.")
        return True
    else:
        print(f"Warning: Target pattern not found in {os.path.basename(filepath)}. Already modified?")
        return False

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cb_dir = os.path.join(root_dir, "third_party", "car-bench")
    
    if not os.path.exists(cb_dir):
        print("third_party/car-bench does not exist. Please run setup first.")
        sys.exit(1)
        
    print("Applying compatibility patches to third_party/car-bench...")
    
    # 1. Patch fixed_context.py (relax constraints)
    fixed_context_path = os.path.join(cb_dir, "car_bench", "envs", "car_voice_assistant", "context", "fixed_context.py")
    target_1 = """    battery_capacity_kwh: float = Field(
        default=80, ge=60, le=100, description="Total (brutto) battery capacity in kWh"
    )
    useable_battery_percentage: float = Field(
        default=95, ge=90, le=100, description="Percentage of battery that's usable"
    )
    max_charging_power_ac: Literal[11, 22] = Field(
        default=11, description="Maximum charging power in kW for AC charging"
    )
    max_charging_power_dc: Literal[150, 200, 250, 268, 300, 350, 1000] = Field(
        default=250, description="Maximum charging power in kW for DC charging"
    )
    energy_consumption: float = Field(
        default=15, ge=10, le=20, description="Power consumption in kWh/100km"
    )
    charging_curve_parameters: Dict[str, List[float]] = Field(
        default_factory=lambda: {
            "soc_tresholds": [5, 10, 20, 50, 70, 80, 90, 95, 100],
            "power_percentages": [60, 90, 100, 100, 100, 90, 70, 40, 20],
        },
        description="Charging curve parameters",
    )
    state_of_charge: float = Field(
        default=10, ge=10, le=100, description="State of charge of the battery"
    )"""
    
    replacement_1 = """    battery_capacity_kwh: float = Field(
        default=80, ge=0, le=500, description="Total (brutto) battery capacity in kWh"
    )
    useable_battery_percentage: float = Field(
        default=95, ge=0, le=100, description="Percentage of battery that's usable"
    )
    max_charging_power_ac: Literal[11, 22] = Field(
        default=11, description="Maximum charging power in kW for AC charging"
    )
    max_charging_power_dc: Literal[150, 200, 250, 268, 300, 350, 1000] = Field(
        default=250, description="Maximum charging power in kW for DC charging"
    )
    energy_consumption: float = Field(
        default=15, ge=0, le=100, description="Power consumption in kWh/100km"
    )
    charging_curve_parameters: Dict[str, List[float]] = Field(
        default_factory=lambda: {
            "soc_tresholds": [5, 10, 20, 50, 70, 80, 90, 95, 100],
            "power_percentages": [60, 90, 100, 100, 100, 90, 70, 40, 20],
        },
        description="Charging curve parameters",
    )
    state_of_charge: float = Field(
        default=10, ge=0, le=100, description="State of charge of the battery"
    )"""
    patch_file(fixed_context_path, target_1, replacement_1)

    # 2. Patch types.py (make calendar_id optional)
    types_path = os.path.join(cb_dir, "car_bench", "types.py")
    target_2 = "    calendar_id: str"
    replacement_2 = "    calendar_id: Optional[str] = None"
    patch_file(types_path, target_2, replacement_2)

    # 3. Patch env.py (update default dataset repo id to carbench-ijcai/car-benchmark-vv)
    env_path = os.path.join(cb_dir, "car_bench", "envs", "car_voice_assistant", "env.py")
    target_3 = 'HF_DATASET_REPO_ID = "johanneskirmayr/car-bench-dataset"'
    replacement_3 = 'HF_DATASET_REPO_ID = "carbench-ijcai/car-benchmark-vv"'
    patch_file(env_path, target_3, replacement_3)

    # 4. Patch user.py (add litellm.drop_params = True for OpenAI models support)
    user_path = os.path.join(cb_dir, "car_bench", "envs", "user", "user.py")
    target_4 = "import litellm"
    replacement_4 = "import litellm\nlitellm.drop_params = True"
    patch_file(user_path, target_4, replacement_4)

    # 5. Patch run.py (Windows compatibility changes and drop_params)
    run_path = os.path.join(cb_dir, "run.py")
    
    # Enable drop_params in run.py
    patch_file(run_path, "import litellm", "import litellm\nlitellm.drop_params = True")
    
    # Windows system encoding
    target_encoding = """if __name__ == "__main__":"""
    replacement_encoding = """if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")"""
    patch_file(run_path, target_encoding, replacement_encoding)
    
    print("Patches application completed!")

if __name__ == "__main__":
    main()
