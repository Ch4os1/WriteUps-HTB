def generate_gu_codes():
    codes = []
    for year in range(2024, 2025):  # 2000 to 2025 inclusive
        for number in range(1, 1000):  # 001 to 999
            code = f"GU{year}{number:03d}"
            codes.append(code)
    return codes

# Generate the list
gu_codes = generate_gu_codes()


for code in gu_codes:
    print(code)

#print(f"\nTotal codes generated: {len(gu_codes)}")
