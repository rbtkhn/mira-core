from datetime import date, datetime, timedelta, timezone

import pytest
import journal_calendar as calendar
import session_checkpoints as checkpoints
import mira_journal as journal
import dream_eod


def test_transition_has_no_gap_or_overlap():
    days = [date(2026, 9, n) for n in range(3, 8)]
    windows = [calendar.day_bounds(day) for day in days]
    assert all(a[1] == b[0] for a, b in zip(windows, windows[1:]))
    assert [(b-a).total_seconds()/3600 for a,b in windows] == [24,24,22,24,24]
    assert windows[2] == (datetime(2026,9,5,6,tzinfo=timezone.utc), datetime(2026,9,6,4,tzinfo=timezone.utc))
    for day, (start,end) in zip(days,windows):
        assert calendar.current_date(start) == day
        assert calendar.current_date(end-timedelta(microseconds=1)) == day
        assert calendar.current_date(end) == day+timedelta(days=1)


@pytest.mark.parametrize('day,hours', [(date(2026,3,8),23), (date(2026,11,1),25), (date(2027,3,14),23)])
def test_daylight_saving_uses_real_zone_rules(day,hours):
    start,end = calendar.day_bounds(day)
    assert (end-start).total_seconds() == hours*3600


def test_transition_checkpoint_binds_calendar_and_rejects_old_bounds(tmp_path):
    day=date(2026,9,5);start,end=calendar.day_bounds(day)
    registry={'sessions': []}
    cp,chunks=checkpoints.build(tmp_path,str(day),start,end,end,registry)
    assert cp['timezone']=='America/New_York'
    assert cp['calendar']['transition_day']
    binding=checkpoints.publish(tmp_path,cp,chunks)
    assert checkpoints.checked(tmp_path,binding)[0]==cp
    with pytest.raises(ValueError,match='boundaries'):
        checkpoints.build(tmp_path,str(day),start,end+timedelta(hours=2),end+timedelta(hours=2),registry)


def test_historical_context_retains_denver_and_future_context_binds_policy(monkeypatch):
    monkeypatch.setattr(journal,'git_commits',lambda *args: [])
    for day in [date(2026,9,4),date(2026,9,5),date(2026,9,6)]:
        start,end=calendar.day_bounds(day)
        activity=journal.collect_activity(day,as_of=end,token_budget=10000,sources=[])
        pack=journal.context_pack(day,activity,10000)
        assert pack['timezone']==calendar.timezone_name(day)
        assert not journal.validate_context_pack(pack)
        if day>=calendar.TRANSITION_DAY:
            assert activity['coverage']['calendar']==calendar.metadata(day)
        else:
            assert 'calendar' not in activity['coverage']


def test_dream_defaults_follow_date_and_reject_mismatched_future_zone(monkeypatch,capsys):
    seen=[]
    monkeypatch.setattr(dream_eod,'check_projection',lambda args,day: seen.append((day,args.timezone)) or {'status':'ready'})
    assert dream_eod.main(['--date','2026-09-04','--check','--json'])==0
    assert dream_eod.main(['--date','2026-09-05','--check','--json'])==0
    assert seen==[('2026-09-04','America/Denver'),('2026-09-05','America/New_York')]
    assert dream_eod.main(['--date','2026-09-06','--timezone','America/Denver','--check'])==1
    assert len(seen)==2
