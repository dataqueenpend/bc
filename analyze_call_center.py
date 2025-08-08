#!/usr/bin/env python3
"""
Script to analyze call center dataset for outbound sales calls and objection handling.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datasets import load_dataset
import re
import json
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Set up plotting
plt.style.use('default')
sns.set_palette("husl")

class CallCenterAnalyzer:
    def __init__(self):
        self.dataset = None
        self.df = None
        self.outbound_sales_calls = None
        self.objection_patterns = {
            'price_objections': [
                r"too expensive", r"can't afford", r"price is high", r"costs too much",
                r"budget", r"cheaper option", r"too costly", r"expensive"
            ],
            'time_objections': [
                r"no time", r"busy", r"call back later", r"not a good time",
                r"in a meeting", r"too busy"
            ],
            'trust_objections': [
                r"don't trust", r"scam", r"not interested", r"sounds fishy",
                r"too good to be true", r"suspicious"
            ],
            'authority_objections': [
                r"need to discuss", r"talk to my", r"spouse", r"manager",
                r"decision maker", r"not my decision"
            ],
            'need_objections': [
                r"don't need", r"already have", r"not looking", r"satisfied with current"
            ]
        }
        
        self.handling_techniques = {
            'acknowledge_and_redirect': [
                r"I understand", r"I hear you", r"that's a valid concern",
                r"many people feel that way", r"let me address that"
            ],
            'question_technique': [
                r"what if I told you", r"have you considered", r"what would it take",
                r"suppose", r"imagine if"
            ],
            'value_demonstration': [
                r"the value you get", r"return on investment", r"save money",
                r"benefit", r"advantage"
            ],
            'social_proof': [
                r"other customers", r"testimonial", r"case study", r"similar situation",
                r"many clients"
            ],
            'urgency_scarcity': [
                r"limited time", r"only today", r"expires", r"while supplies last",
                r"exclusive offer"
            ]
        }
    
    def download_dataset(self):
        """Download the dataset from Hugging Face"""
        print("Downloading dataset from Hugging Face...")
        try:
            self.dataset = load_dataset("AIxBlock/92k-real-world-call-center-scripts-english")
            print(f"Dataset downloaded successfully!")
            print(f"Dataset structure: {self.dataset}")
            
            # Convert to pandas DataFrame
            self.df = pd.DataFrame(self.dataset['train'])
            print(f"Dataset shape: {self.df.shape}")
            print(f"Columns: {self.df.columns.tolist()}")
            
            return True
        except Exception as e:
            print(f"Error downloading dataset: {e}")
            return False
    
    def explore_dataset(self):
        """Explore the dataset structure and content"""
        print("\n=== DATASET EXPLORATION ===")
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {self.df.columns.tolist()}")
        print("\nFirst few rows:")
        print(self.df.head())
        
        print("\nData types:")
        print(self.df.dtypes)
        
        print("\nMissing values:")
        print(self.df.isnull().sum())
        
        # Look at sample conversations
        print("\nSample conversations:")
        for i in range(min(3, len(self.df))):
            print(f"\n--- Sample {i+1} ---")
            for col in self.df.columns:
                if pd.notna(self.df.iloc[i][col]):
                    print(f"{col}: {str(self.df.iloc[i][col])[:200]}...")
    
    def identify_outbound_sales_calls(self):
        """Identify outbound sales calls from the dataset"""
        print("\n=== IDENTIFYING OUTBOUND SALES CALLS ===")
        
        # Keywords that indicate outbound sales calls
        outbound_keywords = [
            r"calling to offer", r"special promotion", r"limited time offer",
            r"exclusive deal", r"new product", r"upgrade", r"discount",
            r"save money", r"interested in", r"would you like",
            r"calling from", r"representative", r"sales", r"offer"
        ]
        
        # Create a pattern to match outbound sales indicators
        outbound_pattern = '|'.join(outbound_keywords)
        
        # Find text column (might be named differently)
        text_column = None
        for col in self.df.columns:
            if 'script' in col.lower() or 'conversation' in col.lower() or 'text' in col.lower():
                text_column = col
                break
        
        if text_column is None:
            # Try the first string column
            for col in self.df.columns:
                if self.df[col].dtype == 'object':
                    text_column = col
                    break
        
        if text_column is None:
            print("Could not find text column in dataset")
            return
        
        print(f"Using column '{text_column}' for analysis")
        
        # Filter for outbound sales calls
        self.df['is_outbound_sales'] = self.df[text_column].str.contains(
            outbound_pattern, case=False, na=False, regex=True
        )
        
        self.outbound_sales_calls = self.df[self.df['is_outbound_sales'] == True].copy()
        
        print(f"Total calls: {len(self.df)}")
        print(f"Outbound sales calls identified: {len(self.outbound_sales_calls)}")
        print(f"Percentage: {len(self.outbound_sales_calls)/len(self.df)*100:.1f}%")
        
        # Save text column name for later use
        self.text_column = text_column
    
    def analyze_objections_and_handling(self):
        """Analyze objections and handling techniques in outbound sales calls"""
        print("\n=== ANALYZING OBJECTIONS AND HANDLING TECHNIQUES ===")
        
        if self.outbound_sales_calls is None or len(self.outbound_sales_calls) == 0:
            print("No outbound sales calls found to analyze")
            return
        
        results = []
        
        for idx, row in self.outbound_sales_calls.iterrows():
            conversation = str(row[self.text_column]).lower()
            
            # Detect objections
            objections_found = {}
            for obj_type, patterns in self.objection_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, conversation):
                        objections_found[obj_type] = objections_found.get(obj_type, 0) + 1
            
            # Detect handling techniques
            techniques_found = {}
            for tech_type, patterns in self.handling_techniques.items():
                for pattern in patterns:
                    if re.search(pattern, conversation):
                        techniques_found[tech_type] = techniques_found.get(tech_type, 0) + 1
            
            if objections_found or techniques_found:
                results.append({
                    'call_id': idx,
                    'conversation': conversation[:500],  # First 500 chars
                    'objections': objections_found,
                    'handling_techniques': techniques_found,
                    'objection_count': sum(objections_found.values()),
                    'technique_count': sum(techniques_found.values())
                })
        
        self.analysis_results = results
        print(f"Analyzed {len(results)} calls with objections or handling techniques")
        
        return results
    
    def group_and_analyze_impact(self):
        """Group objection handling techniques and analyze their impact"""
        print("\n=== GROUPING TECHNIQUES AND ANALYZING IMPACT ===")
        
        if not hasattr(self, 'analysis_results'):
            print("No analysis results available")
            return
        
        # Count objection types
        objection_counts = Counter()
        technique_counts = Counter()
        technique_effectiveness = defaultdict(list)
        
        for result in self.analysis_results:
            for obj_type, count in result['objections'].items():
                objection_counts[obj_type] += count
            
            for tech_type, count in result['handling_techniques'].items():
                technique_counts[tech_type] += count
                
                # Simple effectiveness metric: ratio of techniques to objections
                effectiveness = result['technique_count'] / max(result['objection_count'], 1)
                technique_effectiveness[tech_type].append(effectiveness)
        
        # Create summary dataframes
        self.objection_summary = pd.DataFrame([
            {'objection_type': obj_type, 'count': count, 'percentage': count/sum(objection_counts.values())*100}
            for obj_type, count in objection_counts.most_common()
        ])
        
        self.technique_summary = pd.DataFrame([
            {
                'technique_type': tech_type, 
                'count': count, 
                'percentage': count/sum(technique_counts.values())*100,
                'avg_effectiveness': np.mean(technique_effectiveness[tech_type]) if technique_effectiveness[tech_type] else 0
            }
            for tech_type, count in technique_counts.most_common()
        ])
        
        print("\nMost Common Objections:")
        print(self.objection_summary)
        
        print("\nMost Used Handling Techniques:")
        print(self.technique_summary)
        
        return self.objection_summary, self.technique_summary
    
    def create_visualizations(self):
        """Create visualizations of the analysis"""
        print("\n=== CREATING VISUALIZATIONS ===")
        
        if not hasattr(self, 'objection_summary') or not hasattr(self, 'technique_summary'):
            print("No summary data available for visualization")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Objection types distribution
        if len(self.objection_summary) > 0:
            ax1.bar(self.objection_summary['objection_type'], self.objection_summary['count'])
            ax1.set_title('Distribution of Objection Types')
            ax1.set_xlabel('Objection Type')
            ax1.set_ylabel('Count')
            ax1.tick_params(axis='x', rotation=45)
        
        # Handling techniques distribution
        if len(self.technique_summary) > 0:
            ax2.bar(self.technique_summary['technique_type'], self.technique_summary['count'])
            ax2.set_title('Distribution of Handling Techniques')
            ax2.set_xlabel('Technique Type')
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
        
        # Technique effectiveness
        if len(self.technique_summary) > 0:
            ax3.bar(self.technique_summary['technique_type'], self.technique_summary['avg_effectiveness'])
            ax3.set_title('Average Effectiveness of Techniques')
            ax3.set_xlabel('Technique Type')
            ax3.set_ylabel('Effectiveness Score')
            ax3.tick_params(axis='x', rotation=45)
        
        # Objection vs Technique correlation
        if hasattr(self, 'analysis_results'):
            objection_counts = [result['objection_count'] for result in self.analysis_results]
            technique_counts = [result['technique_count'] for result in self.analysis_results]
            ax4.scatter(objection_counts, technique_counts, alpha=0.6)
            ax4.set_title('Objections vs Handling Techniques')
            ax4.set_xlabel('Number of Objections')
            ax4.set_ylabel('Number of Techniques Used')
        
        plt.tight_layout()
        plt.savefig('/workspace/call_center_analysis.png', dpi=300, bbox_inches='tight')
        print("Visualization saved to call_center_analysis.png")
    
    def generate_detailed_examples(self):
        """Generate detailed examples of objection handling"""
        print("\n=== GENERATING DETAILED EXAMPLES ===")
        
        if not hasattr(self, 'analysis_results'):
            print("No analysis results available")
            return
        
        examples = []
        
        # Find best examples for each objection type
        for obj_type in self.objection_patterns.keys():
            best_example = None
            best_score = 0
            
            for result in self.analysis_results:
                if obj_type in result['objections'] and result['technique_count'] > 0:
                    score = result['technique_count'] / result['objection_count']
                    if score > best_score:
                        best_score = score
                        best_example = result
            
            if best_example:
                examples.append({
                    'objection_type': obj_type,
                    'conversation_snippet': best_example['conversation'][:300],
                    'objections_detected': best_example['objections'],
                    'techniques_used': best_example['handling_techniques'],
                    'effectiveness_score': best_score
                })
        
        self.examples = examples
        
        print(f"Generated {len(examples)} detailed examples")
        for example in examples:
            print(f"\n--- {example['objection_type'].upper()} OBJECTION EXAMPLE ---")
            print(f"Effectiveness Score: {example['effectiveness_score']:.2f}")
            print(f"Conversation: {example['conversation_snippet']}...")
            print(f"Objections: {example['objections_detected']}")
            print(f"Techniques: {example['techniques_used']}")
        
        return examples
    
    def save_results(self):
        """Save analysis results to files"""
        print("\n=== SAVING RESULTS ===")
        
        # Save summary statistics
        summary = {
            'total_calls': len(self.df),
            'outbound_sales_calls': len(self.outbound_sales_calls) if self.outbound_sales_calls is not None else 0,
            'calls_with_objections': len(self.analysis_results) if hasattr(self, 'analysis_results') else 0
        }
        
        with open('/workspace/analysis_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        # Save detailed results
        if hasattr(self, 'objection_summary'):
            self.objection_summary.to_csv('/workspace/objection_summary.csv', index=False)
        
        if hasattr(self, 'technique_summary'):
            self.technique_summary.to_csv('/workspace/technique_summary.csv', index=False)
        
        if hasattr(self, 'examples'):
            with open('/workspace/detailed_examples.json', 'w') as f:
                json.dump(self.examples, f, indent=2)
        
        print("Results saved to:")
        print("- analysis_summary.json")
        print("- objection_summary.csv")
        print("- technique_summary.csv")
        print("- detailed_examples.json")
        print("- call_center_analysis.png")

def main():
    """Main function to run the analysis"""
    analyzer = CallCenterAnalyzer()
    
    # Download and explore dataset
    if not analyzer.download_dataset():
        print("Failed to download dataset")
        return
    
    analyzer.explore_dataset()
    
    # Identify outbound sales calls
    analyzer.identify_outbound_sales_calls()
    
    # Analyze objections and handling
    analyzer.analyze_objections_and_handling()
    
    # Group and analyze impact
    analyzer.group_and_analyze_impact()
    
    # Create visualizations
    analyzer.create_visualizations()
    
    # Generate detailed examples
    analyzer.generate_detailed_examples()
    
    # Save results
    analyzer.save_results()
    
    print("\n=== ANALYSIS COMPLETE ===")
    print("Check the generated files for detailed results.")

if __name__ == "__main__":
    main()