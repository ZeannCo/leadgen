"""Offline walkthrough using fictional records. No external services are called."""
from datetime import date
import json
from models.filing import Filing
from models.contact import EnrichedContact
from pipeline.gates import gate_name, gate_address, gate_query_dedup
from pipeline.qualification import classify_lead
from pipeline.lead_score import score_lead
from pipeline.router import route_ng


def run_demo():
    today = date(2026, 1, 15)
    records = [
        ('DEMO-001', 'Alex Example', '100 Example Street, Nashville, TN 37211'),
        ('DEMO-002', 'Sam Sample', '200 Example Street, Nashville, TN 37211'),
        ('DEMO-003', 'Alex Example', '100 Example Street, Nashville, TN 37211'),
        ('DEMO-004', 'Example Holdings LLC', '300 Example Street, Nashville, TN 37211'),
    ]
    seen = set()
    output = []
    for case, name, address in records:
        if not gate_name(name) or not gate_address(address):
            output.append({'record': case, 'result': 'data_quality_review'})
            continue
        first, last = name.split(' ', 1)
        if not gate_query_dedup(first, last, address, '37211', seen):
            output.append({'record': case, 'result': 'duplicate'})
            continue
        filing = Filing(case_number=case, tenant_name=name, property_address=address,
                        landlord_name='Example Owner LLC', filing_date=today,
                        state='TN', county='Demo County', notice_type='synthetic',
                        source_url='https://example.com/synthetic')
        quality = classify_lead(state='TN', property_address=address, filing_date=today, today=today)
        score = score_lead(rent=2000, tenant_name=name, lead_date=today, today=today)
        route = route_ng(EnrichedContact(filing=filing, track='ng', property_type='residential'))
        output.append({'record':case,'result':quality.lead_bucket,'score':score,
                       'route':route.pipeline,'outreach':'disabled'})
    return output


if __name__ == '__main__':
    print(json.dumps(run_demo(), indent=2))
