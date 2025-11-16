label_map = {
    # --- ACTOR ---
    'ORGANIZATION': 'ACTOR',
    'GOVERNMENT': 'ACTOR',
    'ROLE': 'ACTOR',
    'STAKEHOLDER': 'ACTOR',

    # --- LEGAL SOURCE ---
    'BILL NAME': 'LEGAL_SOURCE',
    'LAW': 'LEGAL_SOURCE',
    'POLICY': 'LEGAL_SOURCE',
    'DOCUMENT': 'LEGAL_SOURCE',

    # --- TECHNOLOGY ---
    'TECHNOLOGY': 'TECHNOLOGY',
    'GENERAL_PURPOSE_AI': 'TECHNOLOGY',
    'FRONTIER_AI': 'TECHNOLOGY',
    'SYNTHETIC_DATA': 'TECHNOLOGY',
    'TRAINING_DATA': 'TECHNOLOGY',
    'DATA': 'TECHNOLOGY',
    'DATA_TYPE': 'TECHNOLOGY',
    'PUBLIC_DATA': 'TECHNOLOGY',

    # --- REQUIREMENT ---
    'REQUIREMENT': 'REQUIREMENT',
    'PROGRAM': 'REQUIREMENT',
    'STANDARD': 'REQUIREMENT',
    'MECHANISM': 'REQUIREMENT',

    # --- DOMAIN ---
    'TRANSPORTATION': 'DOMAIN',
    'HEALTHCARE': 'DOMAIN',
    'EDUCATION': 'DOMAIN',
    'FINANCE': 'DOMAIN',
    'AGRICULTURE': 'DOMAIN',
    'ENVIRONMENT': 'DOMAIN',
    'MILITARY': 'DOMAIN',
    'JUSTICE': 'DOMAIN',
    'CONSUMER': 'DOMAIN',

    # --- RISK ---
    'SAFETY': 'RISK',
    'PRIVACY': 'RISK',
    'FAIRNESS': 'RISK',
    'HUMAN_RIGHTS': 'RISK',
    'SOCIAL_HARM': 'RISK',
    'PRIVACY_HARM': 'RISK',
    'MISUSE_RISK': 'RISK',
    'ECONOMIC_HARM': 'RISK',
    'SAFETY_HARM': 'RISK',
    'SECURITY_HARM': 'RISK',
    'DISCRIMINATION_HARM': 'RISK',
    'STRUCTURAL_RISK': 'RISK',
    'ALIGNMENT_RISK': 'RISK',
    'AUTONOMY_HARM': 'RISK',

    # --- LIFECYCLE STAGE ---
    'TRAINING_STAGE': 'LIFECYCLE_STAGE',
    'TESTING_STAGE': 'LIFECYCLE_STAGE',
    'RESEARCH_STAGE': 'LIFECYCLE_STAGE',
    'DEPLOYMENT_STAGE': 'LIFECYCLE_STAGE',
    'MONITORING_STAGE': 'LIFECYCLE_STAGE',
    'DECOMMISSION_STAGE': 'LIFECYCLE_STAGE',
}

verb_map = {
    # OBLIGATE — formal “must”, “shall”, duties, mandates
    'require': 'OBLIGATE', 'mandate': 'OBLIGATE', 'obligate': 'OBLIGATE',
    'compel': 'OBLIGATE', 'demand': 'OBLIGATE', 'stipulate': 'OBLIGATE',
    'order': 'OBLIGATE', 'instruct': 'OBLIGATE', 'task': 'OBLIGATE',
    'impose': 'OBLIGATE', 'direct': 'OBLIGATE', 'assign': 'OBLIGATE',
    'need': 'OBLIGATE',

    # REGULATE — oversight, enforcement, compliance, governance
    'regulate': 'REGULATE', 'govern': 'REGULATE', 'enforce': 'REGULATE',
    'oversee': 'REGULATE', 'monitor': 'REGULATE', 'supervise': 'REGULATE',
    'administer': 'REGULATE', 'inspect': 'REGULATE', 'ensure': 'REGULATE',
    'protect': 'REGULATE', 'safeguard': 'REGULATE', 'prevent': 'REGULATE',
    'limit': 'REGULATE', 'control': 'REGULATE', 'counter': 'REGULATE',
    'mitigate': 'REGULATE',

    # AUTHORIZE — allow, permit, fund, expand power, empower agencies
    'authorize': 'AUTHORIZE', 'permit': 'AUTHORIZE', 'allow': 'AUTHORIZE',
    'fund': 'AUTHORIZE', 'appropriate': 'AUTHORIZE', 'allocate': 'AUTHORIZE',
    'award': 'AUTHORIZE', 'empower': 'AUTHORIZE', 'grant': 'AUTHORIZE',
    'exempt': 'AUTHORIZE', 'waive': 'AUTHORIZE',

    # EVALUATE — assess, test, examine, audit, analyze
    'evaluate': 'EVALUATE', 'assess': 'EVALUATE', 'analyze': 'EVALUATE',
    'examine': 'EVALUATE', 'test': 'EVALUATE', 'study': 'EVALUATE',
    'review': 'EVALUATE', 'measure': 'EVALUATE', 'verify': 'EVALUATE',
    'track': 'EVALUATE', 'audit': 'EVALUATE', 'inspect': 'EVALUATE',

    # REPORT — submit information, notify, disclose, file
    'submit': 'REPORT', 'report': 'REPORT', 'notify': 'REPORT',
    'disclose': 'REPORT', 'file': 'REPORT', 'publish': 'REPORT',
    'describe': 'REPORT', 'list': 'REPORT', 'outline': 'REPORT',
    'update': 'REPORT',

    # SUPPORT — promote, assist, encourage, help
    'support': 'SUPPORT', 'encourage': 'SUPPORT', 'promote': 'SUPPORT',
    'assist': 'SUPPORT', 'advance': 'SUPPORT', 'aid': 'SUPPORT',
    'bolster': 'SUPPORT', 'boost': 'SUPPORT', 'facilitate': 'SUPPORT',

    # COORDINATE — collaborate, share, convene jointly
    'coordinate': 'COORDINATE', 'convene': 'COORDINATE', 'share': 'COORDINATE',
    'engage': 'COORDINATE', 'participate': 'COORDINATE', 'consult': 'COORDINATE',
    'involve': 'COORDINATE', 'lead': 'COORDINATE', 'collaborate': 'COORDINATE',

    # RESTRICT — prohibit, ban, deny, limit access
    'prohibit': 'RESTRICT', 'deny': 'RESTRICT', 'restrict': 'RESTRICT',
    'prevent': 'RESTRICT',

    # DEVELOP — create, adopt, build, establish, design, improve
    'develop': 'DEVELOP', 'adopt': 'DEVELOP', 'establish': 'DEVELOP',
    'create': 'DEVELOP', 'build': 'DEVELOP', 'design': 'DEVELOP',
    'improve': 'DEVELOP', 'formulate': 'DEVELOP', 'craft': 'DEVELOP',
    'construct': 'DEVELOP', 'revise': 'DEVELOP', 'modify': 'DEVELOP',
    'expand': 'DEVELOP', 'increase': 'DEVELOP',

    # IMPLEMENT — put into practice, carry out, execute
    'implement': 'IMPLEMENT', 'execute': 'IMPLEMENT', 'apply': 'IMPLEMENT',
    'carry': 'IMPLEMENT', 'operate': 'IMPLEMENT', 'put': 'IMPLEMENT',
    'maintain': 'IMPLEMENT', 'continue': 'IMPLEMENT', 'service': 'IMPLEMENT',

    # USE — straightforward operational use
    'use': 'USE', 'utilize': 'USE', 'employ': 'USE',

    # OTHER — everything else not clearly mappable
}

entity_map = {
    # AI variations
    'artificial intelligence': 'AI',
    'Artificial Intelligence': 'AI',
    'artificial intelligence (AI)': 'AI',
    'artificial intelligence (AI) systems': 'AI',
    
    # GenAI variations
    'Generative AI': 'GenAI',
    'generative AI': 'GenAI',
    'Generative Artificial Intelligence': 'GenAI',
    'generative artificial intelligence': 'GenAI',
    'GenAI systems': 'GenAI',
    'generative AI systems': 'GenAI',
    
    # Government agencies/departments (ACTOR category)
    # Since ORGANIZATION, GOVERNMENT, and ROLE all map to ACTOR,
    # we can canonicalize secretaries to their departments
    'Secretary of Commerce': 'Department of Commerce',
    'Secretary of Defense': 'Department of Defense',
    'Secretary of State': 'Department of State',
    'Secretary of Energy': 'Department of Energy',
    'Secretary of Agriculture': 'Department of Agriculture',
    'Secretary of Transportation': 'Department of Transportation',
    'Secretary of Labor': 'Department of Labor',
    'Secretary of Education': 'Department of Education',
    'Secretary of Health and Human Services': 'Department of Health and Human Services',
    'Secretary of Homeland Security': 'Department of Homeland Security',
    'Secretary of the Treasury': 'Department of the Treasury',
    'Secretary of Veterans Affairs': 'Department of Veterans Affairs',
    'Secretary of the Air Force': 'Department of the Air Force',
    'Secretary of the Navy': 'Department of the Navy',
    'Secretary of the Army': 'Department of the Army',
    'Secretaries of Agriculture and Interior': 'Department of Agriculture',
    'Secretaries of Defense': 'Department of Defense',
    'Secretaries of the Army, Navy, and Air Force': 'Armed Forces',
    'Secretaries': 'federal government',
    'Department of Defence': 'Department of Defense',
    'Defense Department': 'Department of Defense',
    'Commerce': 'Department of Commerce',
    'Treasury': 'Department of the Treasury',
    'Commerce Secretaries': 'Department of Commerce',
    
    # NIST variations
    'National Institute of Standards and Technology': 'NIST',
    'Director of the National Institute of Standards and Technology': 'NIST',
    'Director of NIST': 'NIST',
    'NIST Director': 'NIST',
    'Director of the National Institute on Standards and Technology': 'NIST',
    'National Institute on Standards and Technology': 'NIST',
    'Under Secretary of Commerce for Standards and Technology': 'NIST',
    
    # NSF variations
    'National Science Foundation': 'NSF',
    'Director of the National Science Foundation': 'NSF',
    
    # NSA variations
    'National Security Agency': 'NSA',
    'Director of the National Security Agency': 'NSA',
    
    # CIA variations
    'Central Intelligence Agency': 'CIA',
    'CIA Director': 'CIA',
    'Director of the Central Intelligence Agency': 'CIA',
    
    # FBI variations
    'Federal Bureau of Investigation': 'FBI',
    'Director of the FBI': 'FBI',
    
    # OMB variations
    'Office of Management and Budget': 'OMB',
    'Director of the Office of Management and Budget': 'OMB',
    
    # NIH variations
    'National Institutes of Health': 'NIH',
    'Director of the National Institutes of Health': 'NIH',
    'NIH Director': 'NIH',
    'Director of the National Center': 'NIH',
    
    # FAA variations
    'Federal Aviation Administration': 'FAA',
    'Administrator': 'FAA',
    'Deputy Administrator of the Federal Aviation Administration': 'FAA',
    
    # FEMA variations
    'Federal Emergency Management Agency': 'FEMA',
    'Administrator of FEMA': 'FEMA',
    
    # TSA variations
    'Transportation Security Administration': 'TSA',
    'Administrator of TSA': 'TSA',
    
    # CISA variations
    'Cybersecurity and Infrastructure Security Agency': 'CISA',
    'Director of CISA': 'CISA',
    
    # EPA variations
    'Environmental Protection Agency': 'EPA',
    'Administrator of EPA': 'EPA',
    
    # SBA variations
    'Small Business Administration': 'SBA',
    'Administrator of SBA': 'SBA',
    
    # DEA variations
    'Drug Enforcement Administration': 'DEA',
    'Administrator of DEA': 'DEA',
    
    # IRS variations
    'Internal Revenue Service': 'IRS',
    'Commissioner of Internal Revenue': 'IRS',
    
    # SEC variations
    'Securities and Exchange Commission': 'SEC',
    'SEC Chairman': 'SEC',
    
    # FEC variations
    'Federal Election Commission': 'FEC',
    
    # FinCEN variations
    'Financial Crimes Enforcement Network': 'FinCEN',
    
    # CFPB variations
    'Consumer Financial Protection Bureau': 'CFPB',
    'Bureau of Consumer Financial Protection': 'CFPB',
    
    # GSA variations
    'General Services Administration': 'GSA',
    'administrator of general services': 'GSA',
    
    # GAO variations
    'Government Accountability Office': 'GAO',
    'Comptroller General': 'GAO',
    'Comptroller General of the United States': 'GAO',
    
    # OPM variations
    'Office of Personnel Management': 'OPM',
    'U.S. Office of Personnel Management': 'OPM',
    
    # OSTP variations
    'Office of Science and Technology Policy': 'OSTP',
    'Director of the Office of Science and Technology Policy': 'OSTP',
    
    # Coast Guard variations
    'U.S. Coast Guard': 'Coast Guard',
    'US Coast Guard': 'Coast Guard',
    'Commandant of the Coast Guard': 'Coast Guard',
    'Commandant': 'Coast Guard',
    
    # CBP variations
    'U.S. Customs and Border Protection': 'CBP',
    'Customs and Border Protection': 'CBP',
    'U.S. Border Patrol': 'CBP',
    
    # ICE variations
    'U.S. Immigration and Customs Enforcement': 'ICE',
    'Immigration and Customs Enforcement': 'ICE',
    
    # NRC variations
    'Nuclear Regulatory Commission': 'NRC',
    'Chairman of the NRC': 'NRC',
    
    # USAID variations
    'U.S. Agency for International Development': 'USAID',
    'USAID': 'USAID',
    
    # NASA variations
    'National Aeronautics and Space Administration': 'NASA',
    'Administrator of NASA': 'NASA',
    
    # DFC variations
    'U.S. International Development Finance Corporation': 'DFC',
    'Chief Energy Officer': 'DFC',
    
    
    # DoD variations (only clear spelling/abbreviation variants)
    'Department of Defense': 'DoD',
    'DOD': 'DoD',
    'Defense Department': 'DoD',
    
    # DoD AI-specific offices
    'Chief Digital and AI Officer': 'Chief Digital and Artificial Intelligence Officer',
    'Director of the Chief Digital and Artificial Intelligence Office': 'Chief Digital and Artificial Intelligence Officer',
    
    # Joint AI Center variations
    'Director of the Joint Artificial Intelligence Center': 'Joint Artificial Intelligence Center',
    'Director of the joint Artificial Intelligence center': 'Joint Artificial Intelligence Center',
    
    # Cyber Command variations
    'Commander of the United States Cyber Command': 'United States Cyber Command',
    'Commander of Cyber Command': 'United States Cyber Command',
    'Cyber Command': 'United States Cyber Command',
    
    
    # DHS variations
    'Department of Homeland Security': 'DHS',
    'Homeland Security': 'DHS',
    'Secretary of Homeland Security': 'DHS',
    
    # Military branches and leadership
    'Secretary of the Air Force': 'Air Force',
    'Secretary of the Navy': 'Navy',
    'Secretary of the Army': 'Army',
    'Air Force': 'Air Force',
    'Air National Guard': 'Air National Guard',
    'Air National Guard Director': 'Air National Guard',
    'National Guard': 'National Guard',
    
    # Intelligence Community
    'Office of the Director of National Intelligence': 'National Intelligence',
    'Director of National Intelligence': 'National Intelligence',
    'Principal Deputy Director of National Intelligence': 'National Intelligence',
    'intelligence agencies': 'Intelligence Community',
    'intelligence community': 'Intelligence Community',
    'Intelligence Community': 'Intelligence Community',
    
    # NOAA variations
    'National Oceanic and Atmospheric Administration': 'NOAA',
    'NOAA Administrator': 'NOAA',
    'Administrator of the National Oceanic and Atmospheric Administration': 'NOAA',
    'Under Secretary of Commerce for Oceans and Atmosphere': 'NOAA',
    'National Weather Service': 'NOAA',
    'Climate Prediction Center': 'NOAA',
    'NCCOS': 'NOAA',
    'IOOS': 'NOAA',
    'IOOS Program Office': 'NOAA',
    
    # FBI/Law Enforcement
    'law enforcement': 'law enforcement agencies',
    'law enforcement officials': 'law enforcement agencies',
    'Federal law enforcement agencies': 'law enforcement agencies',
    'law enforcement agencies': 'law enforcement agencies',
    
    # FDA variations
    'Food and Drug Administration': 'FDA',
    'Food & Drug Administration': 'FDA',
    'U.S. Food and Drug Administration': 'FDA',
    
    # FTC variations
    'Federal Trade Commission': 'FTC',
    'FTC Act': 'Federal Trade Commission Act',
    
    # FCC variations
    'Federal Communications Commission': 'FCC',
    
    # State/local government
    'governor': 'Governor',
    'attorney general': 'Attorney General',
    'commissioner': 'Commissioner',
    'mayorâ€™s office': 'Mayor',
    
    # State legislatures (generic terms only)
    'state legislature': 'state legislatures',
    'legislative branch': 'state legislatures',
    
    # Courts (only spelling variants, keep specific courts separate)
    'Federal courts': 'federal courts',
    
    # Congressional leadership
    'Senate President Pro Tempore': 'Speaker of the House',
    'House Speaker': 'Speaker of the House',

    # China variations
    'People\'s Republic of China': 'China',
    'PRC': 'China',
    'Peopleâ€™s Republic of China': 'China',
    'Chinese government': 'China',
    'PRC government': 'China',
    'Communist Party of China': 'China',
    'CPC': 'China',
    
    # CSAM variations
    'child sexual assault material': 'CSAM',
    'AI-generated CSAM': 'CSAM',
    'child pornography': 'CSAM',
    'AI-generated child pornography': 'CSAM',
    'child sexual abuse': 'CSAM',
    
    # Deepfakes variations
    'deepfake technologies': 'deepfakes',
    'digital forgeries': 'deepfakes',
    'deep fakes': 'deepfakes',
    'deepfake content': 'deepfakes',
    'deepfake pornography': 'deepfakes',
    'deep fake technology': 'deepfakes',
    'deep fake images': 'deepfakes',
    
    # Machine Learning
    'machine learning': 'ML',
    'Machine Learning': 'ML',
    'machine-learning': 'ML',
    
    # NSA variations
    'National Security Agency': 'NSA',
    'Director of the National Security Agency': 'NSA',
    
    # CIA variations
    'Central Intelligence Agency': 'CIA',
    'CIA Director': 'CIA',
    'Director of the Central Intelligence Agency': 'CIA',
    
    # OMB variations
    'Office of Management and Budget': 'OMB',
    'Director of the Office of Management and Budget': 'OMB',
    
    # NIH variations
    'National Institutes of Health': 'NIH',
    'Director of the National Institutes of Health': 'NIH',
    'NIH Director': 'NIH',
    
    # NSF variations
    'National Science Foundation': 'NSF',
    'Director of the National Science Foundation': 'NSF',
    
    # Medicare variations
    'Medicare program': 'Medicare',
    'Medicare Advantage': 'Medicare',
    'Medicare Parts A and B': 'Medicare',
    'Medicare Part B': 'Medicare',
    'Medicare part B': 'Medicare',
    'Medicare part D': 'Medicare',
    'Medicare Advantage plans': 'Medicare',
    
    # State variations
    'state agencies': 'state governments',
    'State agencies': 'state governments',
    'state government': 'state governments',
    'State Government': 'state governments',
    'state and local governments': 'state and local governments',
    'State and local election offices': 'state and local governments',
    
    # Federal variations
    'Federal Government': 'federal government',
    'Federal agencies': 'federal agencies',
    'federal departments and agencies': 'federal agencies',
    'Federal entities': 'federal agencies',
    'federal departments': 'federal agencies',
    
    # Autonomous vehicles
    'autonomous vehicles': 'autonomous vehicles',
    'autonomous vehicle': 'autonomous vehicles',
    'automated driving systems': 'autonomous vehicles',
    'automated driving system': 'autonomous vehicles',
    'self-driving': 'autonomous vehicles',
    'driverless-capable vehicle': 'autonomous vehicles',
    
    # Biometric variations
    'biometric data': 'biometric identification',
    'biometric identification': 'biometric identification',
    'biometric identifiers': 'biometric identification',
    'biometric information': 'biometric identification',
    'facial recognition technology': 'facial recognition',
    'facial recognition': 'facial recognition',
    
    # Cybersecurity variations
    'cyber security': 'cybersecurity',
    'Cybersecurity': 'cybersecurity',
    'cyber': 'cybersecurity',
    'cybersecurity threats': 'cybersecurity',
    
    # Privacy variations
    'Data Privacy': 'privacy',
    'data privacy': 'privacy',
    'Privacy': 'privacy',
    'privacy rights': 'privacy',
    'consumer privacy': 'privacy',
    'data protection': 'privacy',
    
    # Transparency variations
    'Transparency': 'transparency',
    'transparency policies': 'transparency',
    'transparency requirements': 'transparency',
    
    # Accountability variations
    'Accountability': 'accountability',
    'accountability mechanisms': 'accountability',
    'accountability framework': 'accountability',
    'public accountability': 'accountability',
    
    # National security
    'national security': 'national security',
    'National security': 'national security',
    'national security interests': 'national security',
    'national security threats': 'national security',
    
    # Discrimination variations
    'algorithmic discrimination': 'discrimination',
    'Algorithmic Discrimination Protections': 'discrimination',
    'discriminatory impacts': 'discrimination',
    'bias': 'discrimination',
    'racial bias': 'discrimination',
    'algorithmic bias': 'discrimination',
    
    # Education variations
    'K-12': 'education',
    'higher education': 'education',
    'educational institutions': 'education',
    'institutions of higher education': 'education',
    
    # Workforce variations
    'workforce development': 'workforce',
    'Workforce Development Program': 'workforce',
    'workforce training': 'workforce',
    
    # Elections variations
    'Federal election': 'elections',
    'federal elections': 'elections',
    'political advertisements': 'elections',
    'political advertisement': 'elections',
    
    # Healthcare variations
    'health care': 'healthcare',
    'Health care': 'healthcare',
    'healthcare services': 'healthcare',
    'health care providers': 'healthcare',
    'healthcare providers': 'healthcare',
    
    # U.S. variations
    'United States': 'U.S. government',
    'U.S': 'U.S. government',
    'US': 'U.S. government',
    'U.S. government': 'U.S. government',
    'US Government': 'U.S. government',
    'U.S. Government': 'U.S. government',
    
    # Armed Forces variations
    'U.S. military': 'Armed Forces',
    'United States military': 'Armed Forces',
    'U.S. Armed Forces': 'Armed Forces',
    'military': 'Armed Forces',
    'military departments': 'Armed Forces',
    
    # Coast Guard variations
    'U.S. Coast Guard': 'Coast Guard',
    'US Coast Guard': 'Coast Guard',
    'Commandant of the Coast Guard': 'Coast Guard',
    
    
    # Copyright variations
    'Copyright Office': 'U.S. Copyright Office',
    'Register of Copyrights': 'U.S. Copyright Office',
    
    # Small business variations
    'Small Business Administration': 'SBA',
    
    # Standards variations
    'international standards': 'standards',
    'technical standards': 'standards',
    'voluntary consensus standards': 'standards',
    
    # Research variations
    'research and development': 'R&D',
    'R&D activities': 'R&D',
    'AI research': 'AI research',
    'AI R&D': 'AI research',
    
    # Training data variations
    'training data': 'training data',
    'AI training data': 'training data',
    'training datasets': 'training data',
    
    # Model variations
    'AI models': 'AI models',
    'AI model': 'AI models',
    'foundation models': 'foundation AI models',
    'frontier models': 'frontier AI models',
    'large language model': 'LLM',
    
    # Weapons variations
    'lethal autonomous weapon systems': 'autonomous weapon systems',
    'autonomous weapon systems': 'autonomous weapon systems',
    'lethal autonomous weapons systems': 'autonomous weapon systems',
    'AI-enabled weapon systems': 'autonomous weapon systems',
    
    # Quantum variations
    'quantum computing': 'quantum technology',
    'quantum information science': 'quantum technology',
    'quantum tech': 'quantum technology',
    'quantum technologies': 'quantum technology',
    
    # Children variations
    'minors': 'children',
    'infants': 'children',
    'children': 'children',
    'adolescents': 'children',
    
    # Stakeholder variations
    'stakeholders': 'stakeholders',
    'stakeholder': 'stakeholders',
    'industry stakeholders': 'stakeholders',
    
    # Risk variations
    'risk assessment': 'risk management',
    'risk management': 'risk management',
    'Risk management': 'risk management',
    'risk mitigation': 'risk management',
    
    # Algorithm variations
    'algorithms': 'algorithms',
    'algorithmic systems': 'algorithms',
    'algorithmic processes': 'algorithms',
    
    # Automated decision systems
    'automated decision systems': 'automated decision systems',
    'automated decision-making systems': 'automated decision systems',
    'Automated Decision System': 'automated decision systems',
    'automated decision-making': 'automated decision systems',
    'algorithmic decision-making': 'automated decision systems',
    
    # Testing variations
    'testing': 'testing and evaluation',
    'evaluation': 'testing and evaluation',
    'Testing': 'testing and evaluation',
    'testing and evaluation': 'testing and evaluation',
    
    # Audit variations
    'audit': 'audits',
    
    # State-specific canonicalization
    'Washington State': 'Washington',
}