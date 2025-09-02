import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from impact_analyzer import ImpactAnalyzer

st.set_page_config(
    page_title="Impact Analysis - Immuta x MFEC Helper",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Impact Analysis")
st.markdown("Compare old vs new YAML files to analyze policy changes indevelopment")

# Create two columns for file uploads
col1, col2 = st.columns(2)

with col1:
    st.subheader("📄 Original YAML")
    original_file = st.file_uploader(
        "Upload original YAML file",
        type=['yaml', 'yml'],
        key="original"
    )
    
    if original_file:
        original_content = original_file.read().decode('utf-8')
        with st.expander("View Original Content"):
            st.code(original_content, language='yaml')

with col2:
    st.subheader("📄 Modified YAML")
    modified_file = st.file_uploader(
        "Upload modified YAML file", 
        type=['yaml', 'yml'],
        key="modified"
    )
    
    if modified_file:
        modified_content = modified_file.read().decode('utf-8')
        with st.expander("View Modified Content"):
            st.code(modified_content, language='yaml')

# Analysis section
if original_file and modified_file:
    if st.button("🔍 Analyze Impact", type="primary"):
        analyzer = ImpactAnalyzer()
        
        with st.spinner("Analyzing changes..."):
            impact = analyzer.analyze_impact(original_content, modified_content)
        
        if "error" in impact:
            st.error(f"❌ {impact['error']}")
        else:
            # Summary section
            st.header("📊 Summary of Changes")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Original Rules", impact['summary']['old_rule_count'])
            with col2:
                st.metric("New Rules", impact['summary']['new_rule_count'])
            with col3:
                st.metric("Rules Added", impact['summary']['rules_added'])
            with col4:
                st.metric("Rules Removed", impact['summary']['rules_removed'])
            
            # Impact level
            impact_level = impact['summary']['impact_level']
            if impact_level == "HIGH":
                st.error(f"🔴 Impact Level: {impact_level}")
            elif impact_level == "MEDIUM":
                st.warning(f"🟡 Impact Level: {impact_level}")
            elif impact_level == "LOW":
                st.info(f"🟢 Impact Level: {impact_level}")
            else:
                st.success(f"✅ Impact Level: {impact_level}")
            
            # Rule changes
            if impact['rule_changes']:
                st.header("📋 Detailed Rule Changes")
                for change in impact['rule_changes']:
                    with st.expander(f"Rule {change['rule_number']} - {change['change_type']}"):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(change['description'])
                        with col2:
                            if change['impact'] == "HIGH":
                                st.error(f"Impact: {change['impact']}")
                            elif change['impact'] == "MEDIUM":
                                st.warning(f"Impact: {change['impact']}")
                            else:
                                st.info(f"Impact: {change['impact']}")
            
            # Access impact
            st.header("🔐 Access Impact Analysis")
            access_impact = impact['access_impact']
            
            if access_impact['access_expanded']:
                st.success("📈 Data access has been EXPANDED")
                st.info("More users may be able to see data with the new policy")
            elif access_impact['access_restricted']:
                st.error("📉 Data access has been RESTRICTED") 
                st.warning("Fewer users may be able to see data with the new policy")
            else:
                st.info("➡️ Data access level remains SIMILAR")
            
            st.write(f"**Description:** {access_impact['description']}")
            
            # Show detailed scenarios if available
            if 'affected_scenarios' in access_impact and access_impact['affected_scenarios']:
                with st.expander("🔍 Detailed Access Scenarios"):
                    for scenario in access_impact['affected_scenarios']:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"**{scenario['user_type']}**")
                        with col2:
                            old_status = "✅ Access" if scenario['old_access'] else "❌ No Access"
                            st.write(f"Before: {old_status}")
                        with col3:
                            new_status = "✅ Access" if scenario['new_access'] else "❌ No Access"
                            st.write(f"After: {new_status}")
                        
                        if scenario['change'] == 'EXPANDED':
                            st.success(f"→ {scenario['user_type']} gained access")
                        else:
                            st.error(f"→ {scenario['user_type']} lost access")
                        st.divider()
            
            # Affected users
            if impact['affected_users']:
                st.header("👥 Potentially Affected User Groups")
                st.warning("The following user groups may be affected by these changes:")
                for user_group in impact['affected_users']:
                    st.write(f"• {user_group}")
            
            # LLM Analysis
            if 'llm_analysis' in impact and impact['llm_analysis']:
                st.header("🤖 AI Analysis")
                st.info(impact['llm_analysis'])
            
            # Recommendations
            st.header("💡 Recommendations")
            
            if impact_level == "HIGH":
                st.error("""
                **High Impact Changes Detected:**
                - Review all changes carefully before deployment
                - Test with affected user groups
                - Consider phased rollout
                - Notify stakeholders about access changes
                """)
            elif impact_level == "MEDIUM":
                st.warning("""
                **Medium Impact Changes Detected:**
                - Review changes with data owners
                - Test with sample users
                - Monitor access patterns after deployment
                """)
            elif impact_level == "LOW":
                st.info("""
                **Low Impact Changes Detected:**
                - Changes appear minimal
                - Standard testing recommended
                - Monitor for unexpected issues
                """)
            else:
                st.success("""
                **No Significant Changes Detected:**
                - Policies appear identical
                - Standard deployment process can be followed
                """)

else:
    # Instructions
    st.info("👆 Please upload both original and modified YAML files to analyze impact")
    
    with st.expander("ℹ️ How Impact Analysis Works"):
        st.markdown("""
        **Impact Analysis examines:**
        
        1. **Rule Changes**: Modifications to policy rules
           - Added/removed/modified predicates
           - Changes to user groups
           - Changes to operators (any/all)
        
        2. **Access Impact**: Effect on data access (using Top-Down Logic)
           - Immuta evaluates rules from top to bottom
           - First matching rule applies, subsequent rules are ignored
           - Analyzes impact based on user scenarios
        
        3. **Affected Users**: User groups that may be impacted
        
        4. **Impact Level**: Severity of changes
           - 🔴 HIGH: Significant changes requiring careful review
           - 🟡 MEDIUM: Moderate changes
           - 🟢 LOW: Minor changes
           - ✅ NONE: No changes detected
        """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by MFEC for Immuta | Data Policy Impact Analysis")