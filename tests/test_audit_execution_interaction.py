"""B09 fixed information, decisions and native bundle gates (DLV-08/09)."""
from dataclasses import replace
import base64
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests/audit_fixtures/sc3_runtime'))
from test_audit_execution_wire import covers
from test_audit_execution_journal import scratch
from test_audit_execution_dispatch import native_request
from test_audit_execution_coordinator import fault_receipt
import dispatch_case as case
import interaction_case as inter
from crucis_causal.execution import api,codec
from crucis_causal.execution.model import contract,identity,known,reference,qualified,index,scope,unknown


def prepare(env,labels=('Q1',)):
    for label in labels:
        acquired=env.run(env.information(label));assert acquired.state=='completed',acquired.issues
        computed=env.run(env.compute(label));assert computed.state=='completed',computed.issues
    env.prepare_decisions();selected=env.select(labels);assert selected.state=='completed',selected.issues
    frozen=env.freeze_choice(selected);assert frozen.state=='completed',frozen.issues
    return selected,frozen.value


def fault(case_id,variant,env,**facts):
    head=env.journal.head(env.account,env.jctx).value
    fault_receipt(case_id,variant,'receiver-oracle',env.client.call('interaction_oracle'))
    fault_receipt(case_id,variant,'history-prefix',{'package':head.snapshot.package_id,'digest':head.snapshot.digest,'bytes':base64.b64encode(head.snapshot.source_bytes).decode()})
    fault_receipt(case_id,variant,'recovered-view',facts)


class InteractionCases(unittest.TestCase):
    @covers('F10','OP29P','OP10P')
    def test_lost_selection_commit_reply_reconciles_original_choice_before_send(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'});job=client.call('oracle')['jobs'][0]['id'];env=inter.Environment(root/'coordinator',client,job)
            self.assertEqual(env.run(env.information()).state,'completed');self.assertEqual(env.run(env.compute()).state,'completed')
            env.prepare_decisions();selected=env.select();occurrence=identity();armed=[True]
            def lose(label):
                if armed[0] and label=='after_journal_commit':armed[0]=False;raise OSError('injected selection commit reply loss')
            env.jctx=replace(env.jctx,fault=lose)
            lost=env.freeze_choice(selected,occurrence=occurrence)
            self.assertEqual(lost.state,'rejected',lost.issues);self.assertEqual(client.call('interaction_oracle')['deliveries'],'0')
            fresh=inter.reopen(env);choice=fresh.freeze_choice(selected,occurrence=occurrence)
            self.assertEqual(choice.state,'completed',choice.issues);self.assertEqual(choice.value['target'],occurrence)
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'0')
            sent=fresh.run(fresh.deliver(choice.value));self.assertEqual(sent.state,'completed',sent.issues)
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'1')
            fault('F10','selection_commit_reply_loss',fresh,choice=choice.value,one_choice=True,no_delivery_before_reconciliation=True)

    @covers('F11','OP10P','OP11P')
    def test_lost_native_delivery_reply_reuses_original_G_D_and_receipt_lookup(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'});job=client.call('oracle')['jobs'][0]['id'];env=inter.Environment(root/'coordinator',client,job)
            _,choice=prepare(env);plan=env.plan(env.deliver(choice));self.assertEqual(plan.state,'completed',plan.issues)
            group,d=identity(),identity();admitted=env.admit(plan.value,group=group);self.assertEqual(admitted.state,'completed',admitted.issues)
            client.call('arm_delivery_loss');lost=env.issue(admitted.value,transmission=d)
            self.assertEqual(lost.state,'partial',lost.issues);self.assertEqual(lost.effects[0].acceptance['state'],'unresolved')
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'1')
            fresh=inter.reopen(env);restored=fresh.coordinator.restore_prepared(plan.value.command,plan.value.source_view,fresh.context.read)
            self.assertEqual(restored.state,'completed',restored.issues)
            new=fresh.admit(restored.value,group=group);self.assertEqual(new.state,'completed',new.issues)
            replay=fresh.issue(new.value,transmission=d);self.assertEqual(replay.state,'partial',replay.issues);self.assertIsNone(replay.value.token.runtime_permit)
            found=fresh.run(fresh.lookup_answer(plan.value.command));self.assertEqual(found.state,'completed',found.issues)
            native=client.call('interaction_oracle');self.assertEqual(native['deliveries'],'1');self.assertEqual(native['physical_messages'],'1')
            self.assertEqual(native['consumed'],'1');self.assertEqual(native['remaining'],'1')
            self.assertLess(int(fresh.owner.remaining_control(fresh.allocation)),1000)
            fault('F11','delivery_commit_before_reply',fresh,transmission=d,same_group=group,no_replay_permit=True,deliveries='1',consumed='1')

    @covers('OP29H','OP10H')
    def test_later_information_cannot_enter_old_frontier_or_replace_frozen_choice(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'});job=client.call('oracle')['jobs'][0]['id'];env=inter.Environment(root/'coordinator',client,job)
            selected,choice=prepare(env)
            from crucis_causal.execution.model import Builder
            b=Builder('Later incompatible decision frontier')
            f=b.add('frontier',{'local_records':index(),'source_positions':index(),'selection_rule':contract('s3.fixture.later_empty_frontier')})
            audience=b.add('audience',{'purpose':contract('s3.private_fixture'),'recipients':index(),'disclosure_policy':inter.unknown_ref('s1.policy'),'authority':unknown()})
            r=b.add('projection_view',{'view_role':'audience_projection','audience':audience,'projection_contract':contract('s3.fixture.later_frontier'),'members':index([f]),'claims':index(),'limits':index()})
            v=case.frame(b,r,env.context.read.views);env.include(v)
            actions=(inter.bound(env.actions['Q1']['action'],'s3.role.actions',env.context.read),);policy=inter.bound(env.policy,'s3.role.policy',env.context.read)
            denied=env.procedure.select(actions,policy,env.information_inputs,qualified(f,v.package_id),env.context.read)
            self.assertEqual(denied.state,'rejected');self.assertEqual(denied.issues[0].code,'s3.decision_information_outside_frontier')
            changed=replace(selected.value,input_frontier=qualified(f,v.package_id))
            self.assertEqual(env.freeze_choice(api.CallResult('completed',changed)).state,'rejected')
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'0')
            native=env.actions['Q1']['native'];client.call('change_action_context',action=native['id'])
            out=env.run(env.deliver(choice));self.assertEqual(out.state,'completed',out.issues);self.assertFalse(out.effects[0].acceptance['value'])
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'0')

    @covers('OP08P','OP09P','OP10P','OP11P','OP29P','OP29H')
    def test_two_same_text_actions_fixed_sources_freeze_then_deliver_one(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'})
            job=client.call('oracle')['jobs'][0]['id'];env=inter.Environment(root/'coordinator',client,job)
            selected,choice=prepare(env)
            q2=env.select(('Q2',));self.assertEqual(q2.state,'partial',q2.issues);self.assertEqual(q2.value.selected['members'],[])
            self.assertEqual(len(selected.value.selected['members']),1)
            self.assertNotEqual(env.actions['Q1']['action'],env.actions['Q2']['action'])
            self.assertEqual(env.native['actions'][0]['question'],env.native['actions'][1]['question'])
            before=client.call('interaction_oracle');self.assertEqual(before['deliveries'],'0');self.assertEqual(before['computations'],'1')
            delivered=env.run(env.deliver(choice));self.assertEqual(delivered.state,'completed',delivered.issues)
            exposures=[r['payload'] for r in delivered.records.records if r['record_type']=='s3.exposure_entry']
            self.assertEqual({p['facet']:p['extent']['value']['text'] for p in exposures},{'transmitted':'1','policy_consumed':'1'})
            self.assertNotIn('used',{p['facet'] for p in exposures})
            native=client.call('interaction_oracle');self.assertEqual(native['physical_messages'],'1');self.assertEqual(native['deliveries'],'1')
            self.assertEqual(native['consumed'],'1');self.assertEqual(native['remaining'],'1');self.assertEqual(native['native_termination']['state'],'unresolved')
            lookup=env.run(env.lookup_answer(delivered.value.command));self.assertEqual(lookup.state,'completed',lookup.issues)
            self.assertEqual(client.call('interaction_oracle')['deliveries'],'1')

    @covers('OP08H','OP09H','OP10H','OP11H','OP29H')
    def test_wrong_provider_missing_source_and_changed_delivery_choice_hold(self):
        with scratch() as root,case.service(root/'provider') as (client,_):
            client.call('launch',**native_request()|{'mode':'interactive'});job=client.call('oracle')['jobs'][0]['id']
            env=inter.Environment(root/'coordinator',client,job)
            self.assertEqual(env.plan(env.information(provider=contract('s3.unsupplied_provider'))).state,'rejected')
            self.assertEqual(env.run(env.information('Q2')).state,'partial')
            self.assertEqual(env.plan(env.compute('Q2')).state,'rejected')
            self.assertEqual(client.call('interaction_oracle')['computations'],'0')
            _,choice=prepare(env)
            request=env.deliver(choice)
            empty=replace(request,roles=tuple({'role':r['role'],'members':index()} if r['role'] in ('s3.role.actions','s3.role.responses') else r for r in request.roles))
            self.assertEqual(env.plan(empty).state,'rejected')
            changed=replace(request,roles=tuple({'role':r['role'],'members':index([env.actions['Q2']['action']])} if r['role']=='s3.role.actions' else r for r in request.roles))
            self.assertEqual(env.plan(changed).state,'rejected')
            lookup=env.lookup_answer(reference(identity(),'effect_command',env.view.package_id))
            self.assertEqual(env.plan(lookup).state,'rejected')
            self.assertEqual(client.call('interaction_oracle')['physical_messages'],'0')

    @covers('X07','OP10P','OP10H')
    def test_composite_is_one_physical_message_and_native_all_or_none(self):
        for expired in (False,True):
            with self.subTest(expired=expired),scratch() as root,case.service(root/'provider') as (client,_):
                client.call('launch',**native_request()|{'mode':'interactive'});job=client.call('oracle')['jobs'][0]['id']
                env=inter.Environment(root/'coordinator',client,job,all_sources=True)
                _,choice=prepare(env,('Q1','Q2'))
                if expired:client.call('expire_action',action=env.actions['Q2']['native']['id'])
                result=env.run(env.deliver(choice,('Q1','Q2')))
                self.assertEqual(result.state,'completed',result.issues)
                native=client.call('interaction_oracle')
                self.assertEqual(native['deliveries'],'0' if expired else '2')
                self.assertEqual(native['physical_messages'],'0' if expired else '1')
                self.assertEqual(result.effects[0].acceptance,known(not expired))
                exposures=[r['payload'] for r in result.records.records if r['record_type']=='s3.exposure_entry']
                self.assertEqual({p['facet']:p['extent']['value']['text'] for p in exposures},
                    {'transmitted':'2','policy_consumed':'0' if expired else '2'})


if __name__=='__main__':unittest.main()
