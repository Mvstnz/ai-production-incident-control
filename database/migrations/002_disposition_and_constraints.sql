CREATE TABLE erp.quality_dispositions(scope_id uuid NOT NULL,disposition_id uuid NOT NULL,lot_id text NOT NULL,inspection_id text NOT NULL,verified boolean NOT NULL,result text NOT NULL CHECK(result='RELEASED'),evidence text NOT NULL,decided_at timestamptz NOT NULL,PRIMARY KEY(scope_id,disposition_id),FOREIGN KEY(scope_id,lot_id) REFERENCES erp.inventory_lots(scope_id,id),FOREIGN KEY(scope_id,inspection_id) REFERENCES erp.quality_inspections(scope_id,id));
CREATE TRIGGER immutable_disposition BEFORE UPDATE ON erp.quality_dispositions FOR EACH ROW EXECUTE FUNCTION ops.reject_mutation();
CREATE FUNCTION ops.protect_plan_payload() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 IF NEW.body IS DISTINCT FROM OLD.body OR NEW.plan_hash<>OLD.plan_hash OR NEW.plan_version<>OLD.plan_version OR NEW.revision<>OLD.revision OR NEW.impact_assessment_id<>OLD.impact_assessment_id THEN RAISE EXCEPTION 'immutable approved plan content'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER immutable_plan_content BEFORE UPDATE ON ops.action_plans FOR EACH ROW EXECUTE FUNCTION ops.protect_plan_payload();
CREATE FUNCTION ops.protect_action_payload() RETURNS trigger LANGUAGE plpgsql AS $$ BEGIN
 IF NEW.payload IS DISTINCT FROM OLD.payload OR NEW.action_type<>OLD.action_type OR NEW.plan_id<>OLD.plan_id OR NEW.action_key<>OLD.action_key OR NEW.required_role IS DISTINCT FROM OLD.required_role THEN RAISE EXCEPTION 'immutable action content'; END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER immutable_action_content BEFORE UPDATE ON ops.incident_actions FOR EACH ROW EXECUTE FUNCTION ops.protect_action_payload();
CREATE FUNCTION erp.check_reservations() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE maximum numeric; reserved numeric;
BEGIN
 SELECT quantity INTO maximum FROM erp.inventory_lots WHERE scope_id=NEW.scope_id AND id=NEW.lot_id FOR UPDATE;
 SELECT COALESCE(sum(quantity),0) INTO reserved FROM erp.inventory_reservations WHERE scope_id=NEW.scope_id AND lot_id=NEW.lot_id;
 IF reserved>maximum THEN RAISE EXCEPTION 'reservations exceed physical inventory' USING ERRCODE='23514'; END IF;
 RETURN NEW;
END $$;
CREATE CONSTRAINT TRIGGER reservation_total AFTER INSERT OR UPDATE ON erp.inventory_reservations DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION erp.check_reservations();
