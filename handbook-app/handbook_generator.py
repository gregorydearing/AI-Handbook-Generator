import os
from typing import List, Dict

# Try to import Google Genai - gracefully handle if not installed
try:
    from google import genai
    from google.genai import types

    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  google-genai not installed. Running in demo mode.")
    print("Install with: pip install google-genai")


class HandbookGenerator:
    def __init__(self):
        """Initialize handbook generator with Google Gemini API"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.demo_mode = False

        if not self.api_key or self.api_key == 'your-api-key-here':
            print("⚠️  No valid GEMINI_API_KEY found - running in DEMO MODE")
            print("To use real AI generation:")
            print("1. Get free API key: https://aistudio.google.com/app/apikey")
            print("2. Add to .env file: GEMINI_API_KEY=your_key_here")
            print("3. Restart the application")
            self.demo_mode = True
        elif not GENAI_AVAILABLE:
            print("⚠️  google-genai library not installed - running in DEMO MODE")
            self.demo_mode = True
        else:
            try:
                # Initialize real API client
                self.client = genai.Client(api_key=self.api_key)
                self.model_name = 'gemini-2.0-flash-exp'
                print("✅ Google Gemini API initialized successfully")
            except Exception as e:
                print(f"⚠️  Could not initialize Gemini API: {e}")
                print("Running in DEMO MODE")
                self.demo_mode = True

    def generate_response(self, query: str, context: List[Dict]) -> str:
        """Generate a response to a query using retrieved context"""

        if self.demo_mode:
            return self._generate_demo_response(query, context)

        # Real API implementation
        if context:
            context_text = "\n\n".join([
                f"[From {ctx['source']}]\n{ctx['text']}"
                for ctx in context
            ])
        else:
            context_text = "No context available."

        prompt = f"""Based on the following context from uploaded documents, please answer the question.

Context:
{context_text}

Question: {query}

Please provide a clear, accurate answer based on the context provided. If the context doesn't contain relevant information, say so."""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text

        except Exception as e:
            error_details = str(e)

            # Check for quota errors and provide helpful message
            if '429' in str(e) or 'quota' in str(e).lower():
                return f"""❌ API Quota Exceeded

You've hit the free tier API limits. Options:

**Option 1: Wait**
Free tier quotas reset every 24 hours. Try again tomorrow.

**Option 2: Create New API Key**
1. Go to https://aistudio.google.com/app/apikey
2. Delete old key and create new one
3. Update your .env file
4. Restart the app

**Option 3: Demo Mode**
The app is currently running with limited quota. For portfolio/demo purposes, you can see sample outputs in demo mode.

Error details: {error_details}"""

            return f"❌ Error: {error_details}\n\nCheck https://aistudio.google.com/app/apikey for API status"

    def generate_handbook(self, topic: str, context: List[Dict]) -> str:
        """Generate a comprehensive handbook"""

        if self.demo_mode:
            print("📝 Generating demo handbook...")
            return self._generate_demo_handbook(topic, context)

        print("📝 Generating handbook using Google Gemini (iterative approach)...")
        return self._generate_real_handbook_iterative(topic, context)

    def _generate_real_handbook_iterative(self, topic: str, context: List[Dict]) -> str:
        """Generate real handbook section by section"""

        sections = [
            ("Introduction", "Comprehensive introduction with background, scope, and importance. 1500+ words."),
            ("Historical Development", "Evolution, milestones, and key developments over time. 2500+ words."),
            ("Theoretical Foundations", "Core theories, concepts, and principles in detail. 4000+ words."),
            ("Practical Applications", "Real-world uses, implementations, and examples. 3000+ words."),
            ("Current State", "Recent developments, trends, and current landscape. 3000+ words."),
            ("Challenges", "Limitations, difficulties, and open problems. 2500+ words."),
            ("Future Directions", "Predictions, trends, and where field is heading. 2000+ words."),
            ("Case Studies", "Detailed examples and demonstrations. 2500+ words."),
            ("Conclusion", "Summary and synthesis of key points. 1000+ words.")
        ]

        handbook_parts = [f"# Handbook: {topic}\n\n## Table of Contents\n\n"]
        for i, (title, _) in enumerate(sections, 1):
            handbook_parts.append(f"{i}. {title}\n")
        handbook_parts.append("\n---\n\n")

        context_text = "\n\n".join([f"[{ctx['source']}]\n{ctx['text']}" for ctx in context])
        total_words = 0

        for section_title, instruction in sections:
            print(f"📝 Generating: {section_title}")

            prompt = f"""Write a detailed section for a professional handbook.

SECTION: {section_title}
REQUIREMENTS: {instruction}

SOURCE MATERIALS:
{context_text}

Write the complete section with proper markdown formatting. Be comprehensive and detailed."""

            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=prompt
                )
                section_text = response.text
                words = len(section_text.split())
                total_words += words

                handbook_parts.append(f"\n## {section_title}\n\n{section_text}\n")
                print(f"   ✓ {words} words (Total: {total_words})")

            except Exception as e:
                print(f"   ✗ Error: {str(e)}")
                handbook_parts.append(f"\n## {section_title}\n\n[Error: {str(e)}]\n")

        # Add references
        sources = list(set([ctx['source'] for ctx in context]))
        handbook_parts.append(f"\n## References\n\nBased on:\n")
        for source in sources:
            handbook_parts.append(f"- {source}\n")

        final = "".join(handbook_parts)
        print(f"\n✅ Handbook complete: {len(final.split())} words")
        return final

    def _generate_demo_response(self, query: str, context: List[Dict]) -> str:
        """Generate demo response when API not available"""

        if context:
            sources = list(set([ctx['source'] for ctx in context]))
            return f"""**DEMO RESPONSE** *(API not configured - showing sample output)*

Based on the documents you've uploaded ({', '.join(sources)}), here's what I found regarding: "{query}"

**Key Points:**
• The uploaded documents contain relevant information about this topic
• Multiple perspectives and approaches are presented in the source materials
• Specific methodologies, frameworks, and examples are discussed

**Context from Documents:**
The materials cover various aspects including theoretical foundations, practical applications, and current research directions. The documents provide both high-level overviews and detailed technical information.

---
*🔧 To get real AI-generated responses:*
1. Get free API key from https://aistudio.google.com/app/apikey
2. Add to .env: `GEMINI_API_KEY=your_key_here`
3. Restart the app"""
        else:
            return "❌ No documents uploaded yet. Please upload PDFs first."

    def _generate_demo_handbook(self, topic: str, context: List[Dict]) -> str:
        """Generate realistic demo handbook"""

        sources = list(set([ctx['source'] for ctx in context])) if context else ["Sample Document"]

        return f"""# Comprehensive Handbook: {topic}

*Generated from: {', '.join(sources)}*

**⚠️ DEMO MODE** - This is sample output. Configure Google Gemini API for real AI-generated content.

---

## Table of Contents

1. Introduction and Overview
2. Historical Development  
3. Theoretical Foundations
4. Practical Applications
5. Current State of the Field
6. Challenges and Limitations
7. Future Directions
8. Case Studies
9. Conclusion

---

## 1. Introduction and Overview

{topic} represents a significant area of study with broad implications across multiple domains. This handbook provides a comprehensive exploration drawing from uploaded source materials.

### Background

Understanding {topic} requires examining both historical context and current developments. The field has evolved considerably, with early foundational work giving way to modern approaches that leverage new technologies and methodologies.

### Scope and Purpose

This handbook serves multiple audiences including:
- Practitioners seeking deeper understanding
- Researchers requiring comprehensive references  
- Students entering the field
- Decision-makers needing informed perspectives

We examine {topic} from multiple angles: historical development, theoretical foundations, practical applications, and future directions.

### Key Themes

Several recurring themes emerge throughout:
- Evolution of theory and practice over time
- Integration of diverse disciplinary perspectives
- Balance between theoretical rigor and practical application
- Ethical considerations and societal impact
- Role of technology in shaping development

---

## 2. Historical Development

### Early Foundations

The roots of {topic} trace back several decades. Early pioneers established foundational concepts that continue to influence modern thinking. Initial approaches were characterized by:

- Manual processes and limited automation
- Small-scale implementations
- Emphasis on theoretical frameworks
- Gradual accumulation of knowledge

### Growth Period

As capabilities expanded, the field experienced significant growth. Key developments included:

**Technological Advances:** Increased computational power enabled new possibilities. Researchers could tackle previously intractable problems, leading to breakthroughs in both theory and practice.

**Methodological Innovation:** New approaches emerged combining insights from multiple disciplines. Cross-pollination between fields proved particularly fruitful.

**Institutional Support:** Universities and industry began investing more heavily, accelerating progress and attracting talent.

### Modern Era

Recent decades have seen explosive growth driven by:
- Computational revolution and data availability
- Interdisciplinary integration
- Commercial interest and investment
- Democratization of tools and techniques

---

## 3. Theoretical Foundations

### Core Concepts

Understanding {topic} requires familiarity with fundamental concepts forming the theoretical backbone.

**Foundational Principles:** The field rests on certain principles that guide both theoretical development and practical implementation. These emerged from decades of research.

**Key Frameworks:** Various frameworks organize thinking and provide structure for analysis. They help practitioners approach problems systematically.

**Mathematical Foundations:** While not all aspects require deep mathematics, certain concepts prove essential for rigorous analysis and optimal implementation.

### Theoretical Models

**Classical Approaches:** Traditional models emphasize structured, rule-based methods. While sometimes rigid, they provide clear guidelines and predictable outcomes.

**Modern Approaches:** Contemporary models emphasize flexibility and learning from data. These have gained prominence due to ability to handle complexity.

**Hybrid Methods:** Recognizing complementary strengths, hybrid approaches combine multiple methods to leverage advantages of each.

---

## 4. Practical Applications

### Industry Applications

{topic} finds application across numerous industries:

**Healthcare:** Diagnostic support, treatment planning, patient monitoring, resource optimization

**Finance:** Fraud detection, risk assessment, trading optimization, personalized advice

**Manufacturing:** Predictive maintenance, quality control, supply chain optimization, process automation

**Technology:** Natural language processing, computer vision, recommendation systems, information retrieval

### Implementation Strategies

Successful implementation requires:

1. **Clear Problem Definition:** Specific objectives, success criteria, stakeholder alignment
2. **Data Strategy:** Collection, quality assurance, storage, privacy/security
3. **Technical Architecture:** Scalability, reliability, performance, cost considerations
4. **Testing & Validation:** Unit testing, integration testing, performance testing, user acceptance

---

## 5. Current State of the Field

### Recent Developments

The field continues rapid evolution with notable trends:

**Increased Sophistication:** Modern systems demonstrate capabilities that seemed impossible years ago, stemming from improved algorithms, data, and hardware.

**Broader Accessibility:** Tools once requiring specialized expertise become accessible to wider audiences, democratizing innovation.

**Cross-Domain Applications:** Solutions increasingly span multiple domains, requiring integration of diverse knowledge.

### Leading Research Areas

**Fundamental Understanding:** Deepening theoretical knowledge provides crucial insights for future developments.

**Practical Improvements:** Making existing approaches more effective, efficient, and applicable through reduced data requirements, improved efficiency, enhanced robustness.

**Novel Approaches:** Exploring entirely new methods that challenge conventional wisdom, occasionally yielding breakthroughs.

---

## 6. Challenges and Limitations

### Technical Challenges

**Scalability:** Handling real-world complexity and volume presents ongoing difficulties with computational resources, data management, and performance.

**Robustness:** Ensuring consistent, reliable performance across diverse conditions remains challenging, especially for edge cases and changing conditions.

**Interpretability:** Understanding why systems produce particular results can be difficult, raising concerns about debugging, trust, compliance, and ethics.

### Practical Challenges

**Implementation Complexity:** Integration with existing systems, change management, maintenance, measurement of impact.

**Resource Requirements:** Financial investment, skilled personnel, development time, operational resources.

**Organizational Factors:** Leadership support, appropriate culture, cross-functional collaboration, willingness to experiment.

### Ethical Considerations

**Fairness and Bias:** Systems may perpetuate biases in data or design, requiring careful attention to collection, testing, transparency, and monitoring.

**Privacy and Security:** Handling sensitive data raises privacy concerns and security risks.

**Employment Impact:** Automation raises questions about economic and social effects.

---

## 7. Future Directions

### Emerging Trends

**Performance Improvements:** Ongoing advances in algorithms, hardware, and data availability will drive continued capability growth.

**Broader Adoption:** As tools become more accessible and value clearer, adoption will expand to new industries and applications.

**Increased Integration:** Solutions will become embedded infrastructure rather than standalone applications.

**Human-AI Collaboration:** Focus on augmenting human capabilities rather than complete automation.

### Research Frontiers

**Fundamental Advances:** Theoretical work may enable breakthrough capabilities.

**Specialized Applications:** Domain-specific approaches may achieve superior performance.

**Novel Architectures:** New architectural approaches may overcome current limitations.

### Predictions

**Near Term (1-3 years):** Incremental improvements, expansion to new domains, better development tools, focus on practical considerations.

**Medium Term (3-7 years):** Potential breakthroughs, mainstream adoption, evolving governance, greater emphasis on ethics.

**Long Term (7+ years):** Fundamental shifts, deep integration into daily life, new challenges, co-evolution with broader trends.

---

## 8. Case Studies

### Healthcare Implementation

A hospital system improved diagnostic accuracy using {topic}, achieving reduced diagnosis time, improved accuracy, and positive ROI within 18 months. Key lessons: clinical involvement, extensive testing, focused application, workflow integration.

### Financial Services  

A company enhanced fraud detection while maintaining customer experience, achieving reduced fraud, lower false positives, improved satisfaction, and substantial savings. Key lessons: balance security with convenience, need for explainability, human-in-loop for edge cases.

### Manufacturing Optimization

A manufacturer reduced downtime through predictive maintenance, extending equipment life and improving efficiency. Key lessons: data quality critical, organizational change management, value of pilots, importance of domain expertise.

---

## 9. Conclusion

### Key Takeaways

This handbook has explored {topic} from multiple perspectives. Key themes include rapid evolution, balance of theory and practice, interdisciplinary nature, implementation challenges, and ethical considerations.

### Looking Forward

The future appears promising but uncertain. Success depends on continued R&D, responsible deployment, collaboration, thoughtful governance, and attention to societal impacts.

### Final Thoughts

{topic} represents powerful tools with significant potential to benefit society. Realizing this while managing risks requires ongoing effort from all stakeholders.

This handbook provides a comprehensive overview, but the field evolves rapidly. Supplement with current research, industry publications, hands-on practice, and community engagement.

---

## 10. References

### Source Materials
{chr(10).join(f'- {source}' for source in sources)}

---

**📊 Handbook Statistics:**
- Approximate word count: 1,800 words (demo version)
- Sections: 9 main sections + references
- Format: Markdown with proper structure

**🔧 Production Version:**
With Google Gemini API configured, this system generates 20,000+ word handbooks with:
- Detailed content based on your specific source documents
- 9 comprehensive sections (1,000-4,000 words each)
- Deep analysis and synthesis of uploaded materials
- Professional academic tone and structure

**To activate full functionality:**
1. Get free API key: https://aistudio.google.com/app/apikey
2. Add to .env: `GEMINI_API_KEY=your_key_here`  
3. Restart application
4. Generate real AI-powered handbooks!

---

*This demo shows the structure and flow. Real handbooks are 10x longer with AI-generated insights from your documents.*
"""
