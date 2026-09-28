from demo import run_demo


def test_offline_flow_deduplicates_and_holds_invalid_identity():
    rows = run_demo()
    assert len(rows) == 4
    assert rows[0]['route'] == 'residential'
    assert rows[0]['outreach'] == 'disabled'
    assert rows[2]['result'] == 'duplicate'
    assert rows[3]['result'] == 'data_quality_review'
