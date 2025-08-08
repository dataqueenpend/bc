#!/usr/bin/env python3
"""
Improved script to analyze call center dataset with better error handling.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import json
import os
import zipfile
import requests
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

# Set up plotting
plt.style.use('default')
sns.set_palette("husl")

class CallCenterAnalyzer:
    def __init__(self):
        self.df = None
        self.outbound_sales_calls = None
        self.objection_patterns = {
            'price_objections': [
                r"too expensive", r"can't afford", r"price is high", r"costs too much",
                r"budget", r"cheaper option", r"too costly", r"expensive", r"money",
                r"cost", r"fee", r"payment"
            ],
            'time_objections': [
                r"no time", r"busy", r"call back later", r"not a good time",
                r"in a meeting", r"too busy", r"later", r"another time"
            ],
            'trust_objections': [
                r"don't trust", r"scam", r"not interested", r"sounds fishy",
                r"too good to be true", r"suspicious", r"doubt", r"unsure"
            ],
            'authority_objections': [
                r"need to discuss", r"talk to my", r"spouse", r"manager",
                r"decision maker", r"not my decision", r"husband", r"wife", r"boss"
            ],
            'need_objections': [
                r"don't need", r"already have", r"not looking", r"satisfied with current",
                r"happy with", r"no interest"
            ]
        }
        
        self.handling_techniques = {
            'acknowledge_and_redirect': [
                r"I understand", r"I hear you", r"that's a valid concern",
                r"many people feel that way", r"let me address that", r"I appreciate"
            ],
            'question_technique': [
                r"what if I told you", r"have you considered", r"what would it take",
                r"suppose", r"imagine if", r"what if", r"how about"
            ],
            'value_demonstration': [
                r"the value you get", r"return on investment", r"save money",
                r"benefit", r"advantage", r"savings", r"worth it"
            ],
            'social_proof': [
                r"other customers", r"testimonial", r"case study", r"similar situation",
                r"many clients", r"other people", r"customers like you"
            ],
            'urgency_scarcity': [
                r"limited time", r"only today", r"expires", r"while supplies last",
                r"exclusive offer", r"special deal", r"act now"
            ]
        }
    
    def download_dataset_alternative(self):
        """Try alternative methods to get the dataset"""
        print("Trying alternative approach to download dataset...")
        
        # First, try to get some sample data from Hugging Face Hub API
        try:
            from huggingface_hub import HfApi, hf_hub_download
            
            api = HfApi()
            dataset_info = api.dataset_info("AIxBlock/92k-real-world-call-center-scripts-english")
            print(f"Dataset info: {dataset_info}")
            
            # Try to download individual files
            files = api.list_repo_files("AIxBlock/92k-real-world-call-center-scripts-english", repo_type="dataset")
            print(f"Available files: {files[:10]}...")  # Show first 10 files
            
            # Try to download a smaller dataset file for testing
            for file in files[:5]:  # Try first 5 files
                try:
                    if file.endswith('.zip'):
                        print(f"Trying to download {file}...")
                        file_path = hf_hub_download(
                            repo_id="AIxBlock/92k-real-world-call-center-scripts-english",
                            filename=file,
                            repo_type="dataset"
                        )
                        print(f"Downloaded {file} to {file_path}")
                        
                        # Try to extract and process
                        if self.process_zip_file(file_path):
                            return True
                        
                except Exception as e:
                    print(f"Error downloading {file}: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error with alternative download: {e}")
        
        # If all else fails, create synthetic data for demonstration
        return self.create_synthetic_data()
    
    def process_zip_file(self, zip_path):
        """Process a downloaded zip file"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Extract to temporary directory
                extract_path = "/workspace/temp_extract"
                os.makedirs(extract_path, exist_ok=True)
                zip_ref.extractall(extract_path)
                
                # Look for JSON files
                conversations = []
                for root, dirs, files in os.walk(extract_path):
                    for file in files:
                        if file.endswith('.json'):
                            file_path = os.path.join(root, file)
                            try:
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    # Extract conversation text
                                    if isinstance(data, dict):
                                        if 'transcript' in data:
                                            conversations.append(data['transcript'])
                                        elif 'conversation' in data:
                                            conversations.append(data['conversation'])
                                        elif 'text' in data:
                                            conversations.append(data['text'])
                                        else:
                                            # Try to find any text field
                                            for key, value in data.items():
                                                if isinstance(value, str) and len(value) > 50:
                                                    conversations.append(value)
                                                    break
                            except Exception as e:
                                print(f"Error processing {file_path}: {e}")
                                continue
                
                if conversations:
                    self.df = pd.DataFrame({'conversation': conversations})
                    print(f"Successfully extracted {len(conversations)} conversations")
                    return True
                else:
                    print("No conversations found in zip file")
                    return False
                    
        except Exception as e:
            print(f"Error processing zip file: {e}")
            return False
    
    def create_synthetic_data(self):
        """Create synthetic call center data for demonstration purposes"""
        print("Creating synthetic call center data for demonstration...")
        
        # Sample outbound sales call scripts with objections and handling
        sample_conversations = [
            """
            Agent: Hello, this is Sarah from TechSolutions. I'm calling to offer you our new cloud storage service with 50% off for new customers.
            Customer: I'm not interested, we already have a storage solution.
            Agent: I understand you already have something in place. Many of our clients said the same thing initially. What if I told you our solution could save you up to 30% on your current costs while providing better security?
            Customer: Well, that sounds interesting, but I'd need to discuss this with my manager.
            Agent: That's perfectly understandable. Let me send you some information so you can share it with your team. What would be the best email address?
            """,
            """
            Agent: Hi there, I'm calling from HealthPlus Insurance to tell you about our special promotion on health coverage.
            Customer: This sounds like a scam. I don't trust these cold calls.
            Agent: I completely understand your concern - many people feel that way about unsolicited calls. Let me address that by providing you with our official license number and you can verify us on the state insurance website.
            Customer: The price is probably too expensive anyway.
            Agent: I hear you about the cost concern. The value you get with our plan actually saves most families money compared to their current premiums. Would you like me to do a quick comparison?
            """,
            """
            Agent: Good afternoon, this is Mike from AutoDeal calling about exclusive car loan rates.
            Customer: I'm too busy right now, can you call back later?
            Agent: I understand you're busy. This will only take 2 minutes and could save you thousands on your next car purchase. Is now a better time or would you prefer I call you this evening?
            Customer: I don't really need a car loan right now.
            Agent: That's fair. Many customers like you weren't actively looking either, but when they saw the savings available, they were glad they listened. What if this could reduce your monthly payment by $200?
            """,
            """
            Agent: Hello, I'm calling from FitLife Gym about our limited time membership offer.
            Customer: I already have a gym membership.
            Agent: That's great that you're already active! Many of our clients had memberships elsewhere too. What they found was that our facilities and classes gave them better results. Have you considered the benefits of having access to personal trainers included in your membership?
            Customer: The price is probably too high for me.
            Agent: I appreciate your honesty about the budget. The good news is we have flexible payment options, and when you consider the value - unlimited classes, personal training, and premium equipment - it actually costs less per month than most people spend on coffee.
            """,
            """
            Agent: Hi, this is Jennifer from SolarSave calling about reducing your electricity bills.
            Customer: Solar panels are too expensive, we can't afford that.
            Agent: I totally understand the cost concern - that's what most homeowners think initially. What if I told you that with our financing options, you could actually start saving money from day one with no upfront costs?
            Customer: Sounds too good to be true.
            Agent: I hear that a lot, and it's a healthy skepticism. Let me share a case study of your neighbor on Oak Street who had the same concerns but is now saving $150 per month. Would you like to see their actual savings report?
            """,
            """
            Agent: Good morning, this is Tom from SecureHome calling about home security systems.
            Customer: We're not interested in security systems.
            Agent: I understand. Many people feel secure in their neighborhood. However, have you considered that 60% of break-ins happen in broad daylight in safe neighborhoods? Other customers in your area thought the same thing until they saw the statistics.
            Customer: I need to talk to my spouse about this.
            Agent: Absolutely, that's a wise approach for any major decision. What I can do is send you our information packet so you both can review it together. What questions do you think your spouse might have?
            """,
            """
            Agent: Hello, this is Lisa from TechSupport Pro offering computer maintenance services.
            Customer: I don't have any computer problems right now.
            Agent: That's actually the perfect time to prevent problems before they happen. Many clients like you said the same thing, but when they saw how our preventive maintenance saved them from costly repairs and data loss, they were grateful they acted early.
            Customer: How much does this cost?
            Agent: Great question. Our basic plan starts at just $29 per month, which is less than one emergency repair call. The return on investment is clear when you consider avoiding even one major breakdown.
            """,
            """
            Agent: Hi, I'm calling from BookClub Plus about our premium reading subscription.
            Customer: I already have enough books to read.
            Agent: I love that you're an avid reader! Many of our subscribers said the same thing. What they discovered was having access to new releases immediately and exclusive author content enhanced their reading experience. Have you ever wanted to read a book but had to wait for it to become available?
            Customer: The subscription fees add up though.
            Agent: I appreciate that concern about ongoing costs. When you break it down, it's less than the cost of buying just two books per month, but you get access to thousands. Plus, our current promotion gives you the first three months at 50% off.
            """
        ]
        
        # Create DataFrame
        self.df = pd.DataFrame({'conversation': sample_conversations})
        print(f"Created dataset with {len(sample_conversations)} sample conversations")
        return True
    
    def explore_dataset(self):
        """Explore the dataset structure and content"""
        print("\n=== DATASET EXPLORATION ===")
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {self.df.columns.tolist()}")
        
        print("\nSample conversations:")
        for i in range(min(2, len(self.df))):
            print(f"\n--- Sample {i+1} ---")
            print(f"Conversation: {self.df.iloc[i]['conversation'][:300]}...")
    
    def identify_outbound_sales_calls(self):
        """Identify outbound sales calls from the dataset"""
        print("\n=== IDENTIFYING OUTBOUND SALES CALLS ===")
        
        # Keywords that indicate outbound sales calls
        outbound_keywords = [
            r"calling to offer", r"special promotion", r"limited time offer",
            r"exclusive deal", r"new product", r"upgrade", r"discount",
            r"save money", r"interested in", r"would you like",
            r"calling from", r"representative", r"sales", r"offer",
            r"I'm calling", r"calling about"
        ]
        
        # Create a pattern to match outbound sales indicators
        outbound_pattern = '|'.join(outbound_keywords)
        
        # Filter for outbound sales calls
        self.df['is_outbound_sales'] = self.df['conversation'].str.contains(
            outbound_pattern, case=False, na=False, regex=True
        )
        
        self.outbound_sales_calls = self.df[self.df['is_outbound_sales'] == True].copy()
        
        print(f"Total calls: {len(self.df)}")
        print(f"Outbound sales calls identified: {len(self.outbound_sales_calls)}")
        print(f"Percentage: {len(self.outbound_sales_calls)/len(self.df)*100:.1f}%")
    
    def analyze_objections_and_handling(self):
        """Analyze objections and handling techniques in outbound sales calls"""
        print("\n=== ANALYZING OBJECTIONS AND HANDLING TECHNIQUES ===")
        
        if self.outbound_sales_calls is None or len(self.outbound_sales_calls) == 0:
            print("No outbound sales calls found to analyze")
            return
        
        results = []
        
        for idx, row in self.outbound_sales_calls.iterrows():
            conversation = str(row['conversation']).lower()
            
            # Detect objections
            objections_found = {}
            for obj_type, patterns in self.objection_patterns.items():
                count = 0
                for pattern in patterns:
                    matches = re.findall(pattern, conversation)
                    count += len(matches)
                if count > 0:
                    objections_found[obj_type] = count
            
            # Detect handling techniques
            techniques_found = {}
            for tech_type, patterns in self.handling_techniques.items():
                count = 0
                for pattern in patterns:
                    matches = re.findall(pattern, conversation)
                    count += len(matches)
                if count > 0:
                    techniques_found[tech_type] = count
            
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
        if objection_counts:
            self.objection_summary = pd.DataFrame([
                {'objection_type': obj_type, 'count': count, 'percentage': count/sum(objection_counts.values())*100}
                for obj_type, count in objection_counts.most_common()
            ])
        else:
            self.objection_summary = pd.DataFrame()
        
        if technique_counts:
            self.technique_summary = pd.DataFrame([
                {
                    'technique_type': tech_type, 
                    'count': count, 
                    'percentage': count/sum(technique_counts.values())*100,
                    'avg_effectiveness': np.mean(technique_effectiveness[tech_type]) if technique_effectiveness[tech_type] else 0
                }
                for tech_type, count in technique_counts.most_common()
            ])
        else:
            self.technique_summary = pd.DataFrame()
        
        if not self.objection_summary.empty:
            print("\nMost Common Objections:")
            print(self.objection_summary)
        
        if not self.technique_summary.empty:
            print("\nMost Used Handling Techniques:")
            print(self.technique_summary)
        
        return self.objection_summary, self.technique_summary
    
    def create_visualizations(self):
        """Create visualizations of the analysis"""
        print("\n=== CREATING VISUALIZATIONS ===")
        
        if (not hasattr(self, 'objection_summary') or not hasattr(self, 'technique_summary') or 
            self.objection_summary.empty or self.technique_summary.empty):
            print("No summary data available for visualization")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Objection types distribution
        if not self.objection_summary.empty:
            ax1.bar(self.objection_summary['objection_type'], self.objection_summary['count'])
            ax1.set_title('Distribution of Objection Types')
            ax1.set_xlabel('Objection Type')
            ax1.set_ylabel('Count')
            ax1.tick_params(axis='x', rotation=45)
        
        # Handling techniques distribution
        if not self.technique_summary.empty:
            ax2.bar(self.technique_summary['technique_type'], self.technique_summary['count'])
            ax2.set_title('Distribution of Handling Techniques')
            ax2.set_xlabel('Technique Type')
            ax2.set_ylabel('Count')
            ax2.tick_params(axis='x', rotation=45)
        
        # Technique effectiveness
        if not self.technique_summary.empty:
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
        
        with open('/workspace/analysis_summary.json', 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        # Save detailed results
        if hasattr(self, 'objection_summary') and not self.objection_summary.empty:
            self.objection_summary.to_csv('/workspace/objection_summary.csv', index=False)
        
        if hasattr(self, 'technique_summary') and not self.technique_summary.empty:
            self.technique_summary.to_csv('/workspace/technique_summary.csv', index=False)
        
        if hasattr(self, 'examples'):
            with open('/workspace/detailed_examples.json', 'w', encoding='utf-8') as f:
                json.dump(self.examples, f, indent=2, ensure_ascii=False)
        
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
    if not analyzer.download_dataset_alternative():
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