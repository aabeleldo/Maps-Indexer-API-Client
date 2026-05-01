input_file = "leads_with_phone.txt"
output_file = "leads_deduplicated.txt"

def parse_leads(filename):
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()

    sections = content.split("=" * 40)
    categories = []
    i = 0
    while i < len(sections):
        header = sections[i].strip()
        if header and i + 1 < len(sections):
            body = sections[i + 1].strip()
            categories.append((header, body))
            i += 2
        else:
            i += 1
    return categories

def deduplicate(categories):
    seen_phones = set()
    deduplicated = {}

    for header, body in categories:
        if not header or "TOTAL LEADS" in header:
            continue

        leads = body.strip().split("\n\n")
        unique_leads = []

        for lead in leads:
            if not lead.strip():
                continue
            phone_line = next((l for l in lead.split("\n") if l.startswith("Phone:")), None)
            phone = phone_line.replace("Phone:", "").strip() if phone_line else None

            if phone and phone not in seen_phones:
                seen_phones.add(phone)
                unique_leads.append(lead.strip())

        if unique_leads:
            deduplicated[header] = unique_leads

    return deduplicated

def write_file(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        total = 0
        for header, leads in data.items():
            f.write(f"{'=' * 40}\n")
            f.write(f"{header} ({len(leads)} leads)\n")
            f.write(f"{'=' * 40}\n\n")
            for lead in leads:
                f.write(lead + "\n\n")
            total += len(leads)
        f.write(f"{'=' * 40}\n")
        f.write(f"TOTAL LEADS: {total}\n")
    print(f"Saved {total} unique leads to {filename}")

categories = parse_leads(input_file)
deduplicated = deduplicate(categories)
write_file(output_file, deduplicated)
