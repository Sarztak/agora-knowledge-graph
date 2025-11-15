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
