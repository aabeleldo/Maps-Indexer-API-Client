input_file = "leads.txt"
with_phone_file = "leads_with_phone.txt"
no_phone_file = "leads_no_phone.txt"

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

def split_leads(categories):
    with_phone = {}
    no_phone = {}

    for header, body in categories:
        if not header or "TOTAL LEADS" in header:
            continue

        leads = body.strip().split("\n\n")
        cat_with = []
        cat_without = []

        for lead in leads:
            if not lead.strip():
                continue
            if "Phone:   N/A" in lead or "Phone:" not in lead:
                cat_without.append(lead.strip())
            else:
                cat_with.append(lead.strip())

        if cat_with:
            with_phone[header] = cat_with
        if cat_without:
            no_phone[header] = cat_without

    return with_phone, no_phone

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
    print(f"Saved {total} leads to {filename}")

categories = parse_leads(input_file)
with_phone, no_phone = split_leads(categories)
write_file(with_phone_file, with_phone)
write_file(no_phone_file, no_phone)
