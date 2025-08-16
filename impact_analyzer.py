import yaml
from typing import Dict, List, Set, Tuple

class ImpactAnalyzer:
    def __init__(self):
        self.changes = []
    
    def analyze_impact(self, old_yaml: str, new_yaml: str) -> Dict:
        """Analyze impact of YAML changes on data access"""
        try:
            old_config = yaml.safe_load(old_yaml)
            new_config = yaml.safe_load(new_yaml)
        except Exception as e:
            return {"error": f"YAML parsing error: {e}"}
        
        old_rules = self._extract_rules(old_config)
        new_rules = self._extract_rules(new_config)
        
        impact = {
            "summary": self._get_summary(old_rules, new_rules),
            "rule_changes": self._compare_rules(old_rules, new_rules),
            "access_impact": self._analyze_access_impact(old_rules, new_rules),
            "affected_users": self._get_affected_users(old_rules, new_rules)
        }
        
        return impact
    
    def _extract_rules(self, config: Dict) -> List[Dict]:
        """Extract rules from configuration"""
        rules = []
        if 'actions' in config:
            for action in config['actions']:
                if 'rules' in action:
                    rules.extend(action['rules'])
        return rules
    
    def _get_summary(self, old_rules: List, new_rules: List) -> Dict:
        """Get high-level summary of changes"""
        return {
            "old_rule_count": len(old_rules),
            "new_rule_count": len(new_rules),
            "rules_added": max(0, len(new_rules) - len(old_rules)),
            "rules_removed": max(0, len(old_rules) - len(new_rules)),
            "impact_level": self._calculate_impact_level(old_rules, new_rules)
        }
    
    def _compare_rules(self, old_rules: List, new_rules: List) -> List[Dict]:
        """Compare individual rules"""
        changes = []
        
        # Check for modified/removed rules
        for i, old_rule in enumerate(old_rules):
            if i < len(new_rules):
                new_rule = new_rules[i]
                rule_changes = self._compare_single_rule(old_rule, new_rule, i + 1)
                if rule_changes:
                    changes.append(rule_changes)
            else:
                changes.append({
                    "rule_number": i + 1,
                    "change_type": "REMOVED",
                    "description": f"Rule {i + 1} was removed",
                    "impact": "HIGH"
                })
        
        # Check for added rules
        for i in range(len(old_rules), len(new_rules)):
            changes.append({
                "rule_number": i + 1,
                "change_type": "ADDED",
                "description": f"New rule {i + 1} was added",
                "impact": "MEDIUM"
            })
        
        return changes
    
    def _compare_single_rule(self, old_rule: Dict, new_rule: Dict, rule_num: int) -> Dict:
        """Compare a single rule between old and new"""
        changes = []
        
        # Compare predicates
        old_predicate = old_rule.get('config', {}).get('predicate', '')
        new_predicate = new_rule.get('config', {}).get('predicate', '')
        if old_predicate != new_predicate:
            changes.append(f"Predicate changed from '{old_predicate}' to '{new_predicate}'")
        
        # Compare inclusions
        old_groups = self._get_groups(old_rule)
        new_groups = self._get_groups(new_rule)
        if old_groups != new_groups:
            added_groups = new_groups - old_groups
            removed_groups = old_groups - new_groups
            if added_groups:
                changes.append(f"Added groups: {', '.join(added_groups)}")
            if removed_groups:
                changes.append(f"Removed groups: {', '.join(removed_groups)}")
        
        # Compare operators
        old_op = old_rule.get('operator', old_rule.get('config', {}).get('operator', 'any'))
        new_op = new_rule.get('operator', new_rule.get('config', {}).get('operator', 'any'))
        if old_op != new_op:
            changes.append(f"Operator changed from '{old_op}' to '{new_op}'")
        
        if changes:
            return {
                "rule_number": rule_num,
                "change_type": "MODIFIED",
                "description": "; ".join(changes),
                "impact": self._assess_rule_impact(changes)
            }
        
        return None
    
    def _get_groups(self, rule: Dict) -> Set[str]:
        """Extract groups from a rule"""
        groups = set()
        inclusions = rule.get('inclusions', rule.get('config', {}).get('inclusions', {}))
        if 'groups' in inclusions:
            groups.update(inclusions['groups'])
        return groups
    
    def _analyze_access_impact(self, old_rules: List, new_rules: List) -> Dict:
        """Analyze impact on data access using top-down rule evaluation"""
        # Simulate access for different user scenarios
        test_users = self._get_test_user_scenarios(old_rules, new_rules)
        
        access_changes = []
        for user in test_users:
            old_result = self._evaluate_user_access(user, old_rules)
            new_result = self._evaluate_user_access(user, new_rules)
            
            if old_result != new_result:
                access_changes.append({
                    "user_type": user["type"],
                    "old_access": old_result,
                    "new_access": new_result,
                    "change": "EXPANDED" if new_result and not old_result else "RESTRICTED"
                })
        
        has_expanded = any(c["change"] == "EXPANDED" for c in access_changes)
        has_restricted = any(c["change"] == "RESTRICTED" for c in access_changes)
        
        return {
            "access_expanded": has_expanded,
            "access_restricted": has_restricted, 
            "access_unchanged": not access_changes,
            "description": self._get_detailed_access_description(access_changes),
            "affected_scenarios": access_changes
        }
    
    def _get_test_user_scenarios(self, old_rules: List, new_rules: List) -> List[Dict]:
        """Generate test user scenarios based on rules"""
        all_groups = set()
        all_attributes = set()
        
        for rules in [old_rules, new_rules]:
            for rule in rules:
                groups = self._get_groups(rule)
                all_groups.update(groups)
                
                inclusions = rule.get('inclusions', rule.get('config', {}).get('inclusions', {}))
                for attr in inclusions.get('attributes', []):
                    all_attributes.add(f"{attr.get('name', '')}={attr.get('value', '')}")
        
        # Create test scenarios
        scenarios = [{"type": "no_access", "groups": set(), "attributes": set()}]
        
        for group in list(all_groups)[:5]:  # Limit to prevent explosion
            scenarios.append({"type": f"group_{group.split('@')[0]}", "groups": {group}, "attributes": set()})
        
        return scenarios
    
    def _evaluate_user_access(self, user: Dict, rules: List) -> bool:
        """Evaluate if user has access using top-down rule evaluation"""
        for rule in rules:
            if self._user_matches_rule(user, rule):
                return True  # First matching rule applies, stop evaluation
        return False
    
    def _user_matches_rule(self, user: Dict, rule: Dict) -> bool:
        """Check if user matches rule conditions"""
        inclusions = rule.get('inclusions', rule.get('config', {}).get('inclusions', {}))
        operator = rule.get('operator', rule.get('config', {}).get('operator', 'any'))
        
        conditions_met = []
        
        # Check group membership
        rule_groups = set(inclusions.get('groups', []))
        if rule_groups:
            conditions_met.append(bool(user['groups'].intersection(rule_groups)))
        
        # Check attributes
        rule_attributes = inclusions.get('attributes', [])
        if rule_attributes:
            for attr in rule_attributes:
                attr_check = f"{attr.get('name', '')}={attr.get('value', '')}"
                conditions_met.append(attr_check in user['attributes'])
        
        if not conditions_met:
            return False
        
        # Apply operator logic
        if operator == 'all':
            return all(conditions_met)
        else:  # 'any'
            return any(conditions_met)
    
    def _get_affected_users(self, old_rules: List, new_rules: List) -> List[str]:
        """Get list of potentially affected user groups"""
        old_groups = set()
        new_groups = set()
        
        for rule in old_rules:
            old_groups.update(self._get_groups(rule))
        
        for rule in new_rules:
            new_groups.update(self._get_groups(rule))
        
        affected = old_groups.symmetric_difference(new_groups)
        return list(affected)
    
    def _calculate_impact_level(self, old_rules: List, new_rules: List) -> str:
        """Calculate overall impact level"""
        if len(old_rules) != len(new_rules):
            return "HIGH"
        
        changes = 0
        for i, old_rule in enumerate(old_rules):
            if i < len(new_rules):
                if self._compare_single_rule(old_rule, new_rules[i], i + 1):
                    changes += 1
        
        if changes == 0:
            return "NONE"
        elif changes <= len(old_rules) * 0.3:
            return "LOW"
        elif changes <= len(old_rules) * 0.7:
            return "MEDIUM"
        else:
            return "HIGH"
    
    def _assess_rule_impact(self, changes: List[str]) -> str:
        """Assess impact level of rule changes"""
        if any("Predicate changed" in change for change in changes):
            return "HIGH"
        elif any("Removed groups" in change for change in changes):
            return "HIGH"
        elif any("Added groups" in change for change in changes):
            return "MEDIUM"
        else:
            return "LOW"
    
    def _get_detailed_access_description(self, access_changes: List[Dict]) -> str:
        """Get detailed description of access changes"""
        if not access_changes:
            return "No significant access changes detected"
        
        expanded = [c for c in access_changes if c["change"] == "EXPANDED"]
        restricted = [c for c in access_changes if c["change"] == "RESTRICTED"]
        
        descriptions = []
        if expanded:
            descriptions.append(f"{len(expanded)} user scenario(s) gained access")
        if restricted:
            descriptions.append(f"{len(restricted)} user scenario(s) lost access")
        
        return "; ".join(descriptions)