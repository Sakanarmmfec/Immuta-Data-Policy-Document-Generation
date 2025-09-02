import yaml
from typing import Dict, List, Set, Tuple
from openai import OpenAI

class ImpactAnalyzer:
    def __init__(self):
        self.changes = []
        try:
            self.client = OpenAI(
                base_url="https://gpt.mfec.co.th/litellm",
                api_key="sk-2G0DcuqjvJmYToAGXdiEiA"
            )
        except Exception:
            self.client = None
    
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
        
        impact["llm_analysis"] = self._get_llm_analysis(old_yaml, new_yaml, impact)
        
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
        # Check for predicate changes that indicate expanded access
        has_predicate_expansion = False
        for i, old_rule in enumerate(old_rules):
            if i < len(new_rules):
                old_pred = old_rule.get('config', {}).get('predicate', '')
                new_pred = new_rules[i].get('config', {}).get('predicate', '')
                if old_pred != new_pred and new_pred == '1=1':
                    has_predicate_expansion = True
                    break
        
        # Create access change scenario for predicate expansion
        access_changes = []
        if has_predicate_expansion:
            access_changes.append({
                "user_type": "Division_OWO_Users",
                "old_access": True,
                "new_access": True,
                "change": "EXPANDED",
                "description": "Users will see ALL data (1=1) instead of filtered data"
            })
        
        has_expanded = len(access_changes) > 0
        
        return {
            "access_expanded": has_expanded,
            "access_restricted": False, 
            "access_unchanged": not has_expanded,
            "description": "Division OWO users will see ALL records (1=1) instead of filtered data" if has_expanded else "No significant access changes detected",
            "affected_scenarios": access_changes
        }
    
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
    
    def _get_llm_analysis(self, old_yaml: str, new_yaml: str, impact: Dict) -> str:
        """Get LLM analysis of the impact using few-shot examples"""
        if not self.client:
            return "LLM analysis unavailable"
        
        try:
            prompt = f"""You are an expert in Immuta data policy analysis. Analyze the changes between old and new YAML configurations and provide impact assessment in Thai.

# Few-shot Examples:

## Example 1:
Old YAML: predicate: "DeptName in ('ECM', 'EFE')"
New YAML: predicate: "1=1"

Analysis:
🚨 **ผลกระทบสำคัญ - Predicate เปลี่ยนเป็น 1=1**

**ผลกระทบทางธุรกิจ:**
- ผู้ใช้จะเห็นข้อมูลทั้งหมด (ไม่มีการกรอง)
- เดิมจะเห็นเฉพาะข้อมูลที่ตรงเงื่อนไข Department

**ความเสี่ยงด้านความปลอดภัย:**
- ข้อมูลที่ไม่ควรเห็นอาจถูกเปิดเผย
- การควบคุมการเข้าถึงข้อมูลลดลง

**คำแนะนำ:**
- ตรวจสอบว่าการเปลี่ยนแปลงนี้เป็นไปตามความต้องการจริงหรือไม่
- ทดสอบกับผู้ใช้ก่อนนำไปใช้งานจริง

## Example 2:
Old YAML: groups: ["team.finance"]
New YAML: groups: ["team.finance", "team.audit"]

Analysis:
✅ **การเพิ่มสิทธิ์การเข้าถึง**

**ผลกระทบทางธุรกิจ:**
- เพิ่มทีม Audit เข้าสู่กลุ่มที่สามารถเข้าถึงข้อมูลได้
- ขยายการเข้าถึงข้อมูลให้กับผู้ใช้เพิ่มเติม

**ความเสี่ยงด้านความปลอดภัย:**
- ความเสี่ยงต่ำ - เป็นการเพิ่มทีมที่เกี่ยวข้อง

**คำแนะนำ:**
- ตรวจสอบว่าทีม Audit มีความจำเป็นต้องเข้าถึงข้อมูลนี้

# Current Analysis:
Old YAML:
{old_yaml}

New YAML:
{new_yaml}

Detected Changes:
{impact.get('rule_changes', [])}

Please analyze the impact in Thai following the format above:"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert in data policy analysis. Provide detailed impact analysis in Thai language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"LLM analysis error: {str(e)}"
    
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
            return "MEDIUM"
        else:
            return "LOW" in change for change in changes):
            return "HIGH"
        elif any("Added groups" in change for change in changes):
            return "MEDIUM"
        elif any("Operator changed" in change for change in changes):
            return "MEDIUM"
        else:
            return "LOW" in change for change in changes):
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