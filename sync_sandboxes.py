from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from core import sessionfac,supabase
import os

load_dotenv(override=True)
 
Session=sessionfac

# ── Sync storage folders → sandboxes table ────────────────────────

from tables import Sandbox

with Session() as session:
    # List all folders/files in the sandboxes bucket
    response = supabase.storage.from_("sandboxes").list()

    print(f"Found {len(response)} items in sandboxes bucket\n")

    for item in response:
        name = item["name"]

        # Check if sandbox with this name already exists in DB
        existing = session.query(Sandbox).filter(Sandbox.name == name).first()

        if existing:
            print(f"Skipping '{name}' — already exists (id: {existing.id})")
            continue

        # Build the public URL to index.html for this sandbox
        sandbox_url = supabase.storage.from_("sandboxes").get_public_url(f"{name}/index.html")

        # Create new sandbox row
        sandbox = Sandbox(
            name=name,
            sandbox_url=sandbox_url,
        )
        session.add(sandbox)
        session.flush()

        print(f"Created sandbox '{name}' → id: {sandbox.id}")
        print(f"   URL: {sandbox_url}")

    session.commit()
    print("\nSync complete!")

    # Show all sandboxes now in DB
    all_sandboxes = session.query(Sandbox).all()
    print(f"\nAll sandboxes in DB ({len(all_sandboxes)} total):")
    for s in all_sandboxes:
        print(f"   - {s.id} | {s.name} | {s.sandbox_url}")