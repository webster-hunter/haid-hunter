"""
NLP-based extraction service.
Replaces Claude API calls for document analysis using offline keyword matching
and lightweight text processing — zero API cost, zero network dependency.
"""

import logging

logger = logging.getLogger(__name__)

# ── Curated keyword lists ──────────────────────────────────────────────────────

SKILLS_LIST = {
    # ── Programming Languages ──────────────────────────────────────────────────
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go",
    "Golang", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB",
    "Perl", "Bash", "Shell", "PowerShell", "Lua", "Haskell", "Elixir", "Erlang",
    "Clojure", "F#", "OCaml", "Groovy", "Dart", "Julia", "Nim", "Zig", "Crystal",
    "Fortran", "COBOL", "Ada", "Assembly", "VHDL", "Verilog", "Prolog",
    "Lisp", "Scheme", "Racket", "Smalltalk", "Tcl", "Awk", "Solidity",
    "Vyper", "WebAssembly", "WASM", "SQL", "PL/SQL",
    "T-SQL", "HiveQL", "Apex", "ABAP", "VBA", "VBScript",
    "Objective-C", "CoffeeScript", "ReasonML", "PureScript",
    "Elm", "ClojureScript", "GDScript", "HLSL", "GLSL", "CUDA", "OpenCL",
    "MicroPython", "CircuitPython", "Arduino", "Processing",

    # ── Frontend Frameworks / Libraries ───────────────────────────────────────
    "React", "React.js", "ReactJS", "Angular", "AngularJS", "Vue", "Vue.js",
    "VueJS", "Next.js", "NextJS", "Nuxt.js", "NuxtJS", "Svelte", "SvelteKit",
    "SolidJS", "Solid.js", "Qwik", "Astro", "Remix", "Gatsby", "Ember.js",
    "EmberJS", "Backbone.js", "BackboneJS", "Preact", "Lit", "Alpine.js",
    "AlpineJS", "HTMX", "Stimulus", "Turbo", "Hotwire", "Mithril", "Inferno",
    "Redux", "Redux Toolkit", "MobX", "Zustand", "Recoil", "Jotai", "XState",
    "React Query", "TanStack Query", "SWR", "Apollo Client", "Urql",
    "jQuery", "Prototype.js",

    # ── Frontend Styling ──────────────────────────────────────────────────────
    "HTML", "HTML5", "CSS", "CSS3", "Sass", "SCSS", "Less", "Stylus",
    "Tailwind", "Tailwind CSS", "Bootstrap", "Foundation", "Bulma",
    "Material UI", "MUI", "Ant Design", "Chakra UI", "Mantine", "Shadcn/ui",
    "Radix UI", "Headless UI", "DaisyUI", "Semantic UI", "Vuetify",
    "PrimeVue", "Quasar", "Element Plus", "Naive UI", "Flowbite",
    "CSS Modules", "Styled Components", "Emotion", "Stitches", "Vanilla Extract",
    "Storybook",

    # ── Backend Frameworks ─────────────────────────────────────────────────────
    "FastAPI", "Django", "Django REST Framework", "DRF", "Flask", "Litestar",
    "Starlette", "Tornado", "Sanic", "Falcon", "Bottle", "Pyramid",
    "Express", "Express.js", "ExpressJS", "NestJS", "Nest.js", "Fastify",
    "Koa", "Hapi", "AdonisJS", "Feathers.js", "Loopback",
    "Spring", "Spring Boot", "Spring MVC", "Spring Security", "Spring Cloud",
    "Micronaut", "Quarkus", "Vert.x", "Dropwizard", "Play Framework",
    "Rails", "Ruby on Rails", "Sinatra", "Hanami",
    "Laravel", "Symfony", "Lumen", "CodeIgniter", "CakePHP", "Slim", "Phalcon",
    "ASP.NET", "ASP.NET Core", ".NET", ".NET Core", "Blazor", "SignalR",
    "Node.js", "NodeJS", "Deno", "Bun",
    "Gin", "Echo", "Fiber", "Chi", "Gorilla", "Beego",
    "Actix", "Rocket", "Axum", "Warp", "Tide",
    "Phoenix", "Plug", "Absinthe",
    "Ktor", "Vapor",

    # ── API Standards and Protocols ────────────────────────────────────────────
    "REST", "RESTful", "GraphQL", "gRPC", "WebSockets", "WebSocket",
    "SOAP", "XML-RPC", "JSON-RPC", "Thrift", "Avro", "Protobuf",
    "Protocol Buffers", "OpenAPI", "Swagger", "AsyncAPI", "RAML",
    "OData", "HAL", "HATEOAS", "tRPC",
    "OAuth", "OAuth2", "OAuth 2.0", "OpenID Connect", "OIDC",
    "JWT", "SAML", "LDAP", "Active Directory", "SSO",
    "HTTP", "HTTPS", "HTTP/2", "HTTP/3", "QUIC",
    "TCP/IP", "UDP", "DNS", "TLS", "SSL", "mTLS",
    "WebRTC", "Server-Sent Events", "SSE",

    # ── Mobile Development ─────────────────────────────────────────────────────
    "iOS", "Android", "React Native", "Flutter", "Xamarin", "Ionic",
    "Capacitor", "Cordova", "PhoneGap", "NativeScript", "Expo",
    "SwiftUI", "UIKit", "AppKit", "Jetpack Compose", "Android SDK",
    "Kotlin Multiplatform", "KMM", "MAUI", ".NET MAUI",
    "Xcode", "Android Studio",

    # ── Data Science / Analytics ───────────────────────────────────────────────
    "NumPy", "Pandas", "Polars", "Dask", "Vaex",
    "Matplotlib", "Seaborn", "Plotly", "Bokeh", "Altair", "Dash",
    "Jupyter", "JupyterLab", "Jupyter Notebook", "IPython",
    "SciPy", "Statsmodels",
    "SQLAlchemy", "Alembic", "Peewee", "Tortoise ORM",

    # ── Machine Learning / AI ─────────────────────────────────────────────────
    "TensorFlow", "PyTorch", "Keras", "JAX", "Flax",
    "Scikit-learn", "sklearn", "XGBoost", "LightGBM", "CatBoost",
    "Hugging Face", "Transformers", "Diffusers", "PEFT",
    "LangChain", "LlamaIndex", "Haystack", "Semantic Kernel",
    "spaCy", "NLTK", "Gensim", "TextBlob", "FastText",
    "OpenCV", "PIL", "Pillow", "torchvision", "Detectron2", "YOLO",
    "MLflow", "Weights & Biases", "W&B", "Neptune",
    "Kubeflow", "Metaflow", "ZenML", "Kedro", "DVC",
    "ONNX", "TensorRT", "TorchServe", "BentoML", "Seldon",
    "Ray", "Ray Tune", "Ray Serve",
    "Optuna", "Hyperopt",
    "FAISS", "Annoy",
    "LLM", "RAG", "fine-tuning", "prompt engineering",
    "reinforcement learning", "computer vision",
    "NLP", "natural language processing",
    "machine learning", "deep learning",

    # ── Data Engineering ──────────────────────────────────────────────────────
    "Apache Spark", "PySpark", "Hadoop", "MapReduce", "HDFS",
    "Apache Flink", "Flink", "Apache Beam", "Beam",
    "Apache Hive", "Hive", "Presto", "Trino", "Apache Druid",
    "Apache Iceberg", "Delta Lake", "Apache Hudi",
    "dbt", "Apache Airflow", "Airflow", "Prefect", "Dagster", "Luigi",
    "Apache NiFi", "Talend", "Informatica", "Fivetran", "Airbyte", "Stitch",

    # ── Testing ───────────────────────────────────────────────────────────────
    "pytest", "unittest", "hypothesis",
    "Jest", "Vitest", "Mocha", "Chai", "Jasmine", "Karma",
    "Cypress", "Playwright", "Selenium", "WebdriverIO", "Puppeteer",
    "Nightwatch.js", "Appium",
    "JUnit", "TestNG", "Mockito", "AssertJ",
    "RSpec", "Minitest", "Capybara",
    "PHPUnit", "Pest", "Behat",
    "xUnit", "NUnit", "MSTest", "SpecFlow",
    "k6", "Locust", "JMeter", "Gatling", "Artillery",
    "Postman", "Insomnia", "Newman", "Pact", "WireMock",
    "Cucumber", "Behave",
    "SonarQube", "SonarCloud", "CodeClimate",
    "ESLint", "Prettier", "Black", "Ruff", "Flake8", "Pylint", "Mypy",
    "Rubocop", "Stylelint",
    "TDD", "BDD", "ATDD", "mutation testing",

    # ── Build Tools / Bundlers / Package Managers ─────────────────────────────
    "Webpack", "Vite", "Rollup", "Parcel", "esbuild", "Turbopack",
    "Gulp", "Grunt",
    "Babel", "SWC",
    "npm", "Yarn", "pnpm",
    "pip", "Poetry", "Pipenv", "uv", "conda", "Anaconda",
    "Maven", "Gradle", "Ant", "SBT",
    "Cargo",
    "Bundler", "RubyGems",
    "Composer",
    "NuGet", "MSBuild",
    "Bazel", "Buck", "Pants", "Nx", "Turborepo", "Lerna",
    "Make", "CMake", "Meson",

    # ── Version Control ────────────────────────────────────────────────────────
    "Git", "GitHub", "GitLab", "Bitbucket", "Mercurial", "SVN",
    "Subversion", "Perforce",
    "Git Flow", "Trunk-based development", "Feature flags",
    "Conventional Commits", "Semantic versioning", "SemVer",

    # ── DevOps / Development Practices ────────────────────────────────────────
    "CI/CD", "Continuous Integration", "Continuous Deployment",
    "Continuous Delivery", "DevOps", "DevSecOps", "GitOps", "MLOps",
    "SRE", "Site Reliability Engineering",
    "Agile", "Scrum", "Kanban", "SAFe", "XP", "Extreme Programming",
    "Lean", "Waterfall",
    "Pair programming", "Code review",
    "Domain-Driven Design", "DDD", "Event-Driven Architecture",
    "Event Sourcing", "CQRS", "Hexagonal Architecture",
    "Clean Architecture", "Microservices", "Monolith", "SOA",
    "Serverless", "12-factor app", "Cloud-native",
    "Blue-green deployment", "Canary deployment",
    "Infrastructure as Code",

    # ── Security ──────────────────────────────────────────────────────────────
    "OWASP", "Penetration testing", "Pen testing",
    "SAST", "DAST", "SCA",
    "Vulnerability scanning", "Threat modeling", "Zero Trust",
    "PKI", "Secrets management",
    "Encryption", "AES", "RSA", "ECC", "SHA", "bcrypt",
    "RBAC", "ABAC", "IAM",
    "GDPR", "HIPAA", "SOC 2", "PCI DSS", "ISO 27001", "FedRAMP",
    "CVE", "CVSS",
    "OAuth", "FIDO2", "WebAuthn", "MFA", "2FA",
    "SIEM", "WAF",

    # ── Databases – Concepts ──────────────────────────────────────────────────
    "SQL", "NoSQL", "NewSQL", "ACID",
    "Database design", "Schema design", "Normalization",
    "Indexing", "Query optimization",
    "Stored procedures", "Transactions", "Replication", "Sharding",
    "ORM", "ActiveRecord", "Sequelize", "TypeORM", "Prisma",
    "Drizzle", "Mongoose",
    "Full-text search", "Vector search",

    # ── Cloud Architecture — Strategies & Patterns ────────────────────────────
    # Well-Architected Framework
    "Well-Architected Framework", "AWS Well-Architected Framework",
    "Well-Architected Review", "Well-Architected Tool",
    "Operational Excellence", "Security pillar", "Reliability pillar",
    "Performance Efficiency", "Cost Optimization pillar", "Sustainability pillar",
    # Migration strategies
    "Cloud migration", "Cloud adoption", "Cloud transformation",
    "AWS Cloud Adoption Framework", "AWS CAF",
    "lift and shift", "rehost", "replatform", "repurchase", "refactor",
    "re-architect", "retire", "retain",
    "migration strategy", "cloud readiness assessment",
    "AWS Migration Hub", "migration factory",
    # Landing Zone / Governance
    "Landing Zone", "AWS Landing Zone", "Control Tower",
    "AWS Control Tower", "multi-account strategy",
    "Service Control Policies", "SCP", "permission boundaries",
    "AWS Organizations", "organizational units", "OU",
    "account vending machine", "guardrails",
    "Cloud Center of Excellence", "CCoE",
    # Availability & Resilience
    "High availability", "HA", "Fault tolerance", "Disaster recovery", "DR",
    "RTO", "RPO", "business continuity", "BCP",
    "multi-region", "multi-AZ", "Availability Zone", "AZ",
    "active-active", "active-passive", "warm standby", "pilot light",
    "hot standby", "cold standby",
    "failover", "failback", "regional failover",
    "chaos engineering", "fault injection", "GameDay",
    "resilience testing", "recovery testing",
    # Scalability & Performance
    "Scalability", "horizontal scaling", "vertical scaling", "Auto-scaling",
    "Auto Scaling Group", "ASG", "target tracking", "step scaling",
    "scheduled scaling", "predictive scaling",
    "load balancing", "Application Load Balancer", "Network Load Balancer",
    "Global Accelerator", "latency-based routing",
    "CDN", "content delivery", "Edge computing", "edge location",
    "caching strategy", "cache invalidation", "TTL",
    # Networking & Connectivity
    "VPC", "Virtual Private Cloud", "VPC design", "subnet design",
    "public subnet", "private subnet", "CIDR", "IP addressing",
    "NAT Gateway", "NAT instance", "Internet Gateway", "egress-only gateway",
    "VPC Peering", "VPC peering", "Transit Gateway", "transit routing",
    "AWS PrivateLink", "VPC endpoint", "interface endpoint", "gateway endpoint",
    "Direct Connect", "AWS Direct Connect", "VPN", "Site-to-Site VPN",
    "Client VPN", "AWS VPN", "CloudWAN", "AWS Cloud WAN",
    "network segmentation", "security groups", "NACLs", "network ACL",
    "Route 53", "DNS failover", "health checks", "latency routing",
    "geolocation routing", "weighted routing", "traffic policies",
    # Security & Identity Architecture
    "Zero Trust", "Zero Trust architecture", "ZTNA",
    "defense in depth", "shared responsibility model",
    "least privilege", "principle of least privilege",
    "identity-based policies", "resource-based policies",
    "cross-account access", "cross-account roles", "assume role",
    "federated access", "federation", "identity federation",
    "service-linked roles", "instance profiles", "IAM roles",
    "tag-based access control", "attribute-based access control",
    "encryption at rest", "encryption in transit", "envelope encryption",
    "key management", "customer-managed keys", "CMK", "KMS",
    "data classification", "data sovereignty", "data residency",
    "compliance automation", "audit logging", "immutable logs",
    "AWS Shield", "DDoS protection", "WAF", "bot protection",
    "AWS Firewall Manager", "AWS Network Firewall",
    # Cost Management
    "FinOps", "cost optimization", "cloud cost management",
    "Reserved Instances", "RI", "Savings Plans",
    "Compute Savings Plans", "EC2 Instance Savings Plans",
    "Spot Instances", "Spot Fleet", "On-Demand",
    "right-sizing", "resource tagging", "cost allocation tags",
    "cost allocation", "showback", "chargeback",
    "AWS Cost Explorer", "AWS Budgets", "AWS Pricing Calculator",
    "Compute Optimizer", "Trusted Advisor",
    # Serverless & Event-Driven
    "Serverless", "serverless architecture", "FaaS",
    "event-driven architecture", "event-driven",
    "Lambda", "AWS Lambda", "Lambda@Edge", "Lambda layers",
    "Step Functions", "state machine", "workflow orchestration",
    "EventBridge", "event bus", "event schema", "event sourcing",
    "SQS", "SNS", "fan-out pattern", "pub/sub pattern",
    "dead letter queue", "DLQ", "FIFO queue", "message deduplication",
    "idempotency", "at-least-once delivery", "exactly-once delivery",
    # Containers & Microservices on AWS
    "ECS", "EKS", "Fargate", "AWS Fargate", "container orchestration",
    "ECR", "container registry", "image scanning",
    "service mesh", "App Mesh", "sidecar proxy",
    "blue-green deployment", "canary deployment", "rolling deployment",
    "infrastructure as code", "immutable infrastructure",
    "GitOps", "ArgoCD", "Flux",
    # Data Architecture on AWS
    "data lake", "data lakehouse", "data mesh", "data warehouse",
    "S3 data lake", "Lake Formation", "AWS Glue", "Glue Catalog",
    "Athena", "serverless query", "Redshift", "Redshift Spectrum",
    "Kinesis Data Streams", "Kinesis Data Firehose", "Kinesis Data Analytics",
    "MSK", "streaming architecture", "lambda architecture", "kappa architecture",
    "CDC", "change data capture", "data replication",
    "ETL", "ELT", "data pipeline", "data integration",
    "data governance", "data catalog", "data lineage",
    # Storage Architecture
    "S3", "object storage", "S3 Intelligent-Tiering", "S3 Standard-IA",
    "S3 One Zone-IA", "S3 Glacier", "S3 Glacier Deep Archive",
    "S3 lifecycle policy", "storage tiering", "data archival",
    "EBS", "EFS", "FSx", "block storage", "file storage",
    "shared file system", "NFS", "SMB",
    # General Cloud Concepts
    "Multi-cloud", "Hybrid cloud", "Cloud-native", "cloud first",
    "microservices", "API-first", "API gateway pattern",
    "strangler fig pattern", "bulkhead pattern", "circuit breaker",
    "retry with backoff", "rate limiting", "throttling",
    "observability", "distributed tracing", "SLO", "SLA", "SLI", "error budget",
    "toil reduction", "runbook", "playbook", "runbook automation",

    # ── Game Development ──────────────────────────────────────────────────────
    "Unity", "Unreal Engine", "Godot", "Phaser", "Babylon.js",
    "Three.js", "WebGL", "OpenGL", "Vulkan", "DirectX",

    # ── Embedded / Systems ────────────────────────────────────────────────────
    "Embedded C", "RTOS", "FreeRTOS", "Zephyr",
    "Raspberry Pi", "ESP32", "STM32",
    "UART", "SPI", "I2C", "CAN bus",
    "Linux kernel", "Device drivers", "Yocto",

    # ── Accessibility ─────────────────────────────────────────────────────────
    "WCAG", "WCAG 2.1", "WCAG 2.2", "ARIA", "WAI-ARIA",
    "Section 508", "Accessibility testing",
    "Inclusive design", "Universal design",

    # ── Design Tools ──────────────────────────────────────────────────────────
    "Figma", "Sketch", "Adobe XD", "InVision", "Zeplin", "Framer",
    "Adobe Photoshop", "Adobe Illustrator",

    # ── Documentation ─────────────────────────────────────────────────────────
    "Markdown", "Sphinx", "MkDocs", "Docusaurus", "GitBook", "Confluence",
    "JSDoc", "TSDoc", "Javadoc", "Swagger UI", "Redoc",

    # ── Low-Code / No-Code / Business Platforms ───────────────────────────────
    "Salesforce", "Salesforce Lightning", "Salesforce Apex",
    "ServiceNow", "OutSystems", "Mendix", "Appian", "Power Apps",
    "Power Automate", "Power BI", "Tableau", "Retool",
    "WordPress", "Shopify", "Zapier",

    # ── Blockchain / Web3 ─────────────────────────────────────────────────────
    "Blockchain", "Ethereum", "Web3.js", "Ethers.js",
    "Hardhat", "Truffle", "Foundry", "OpenZeppelin", "IPFS",
    "Smart contracts",
}


TECHNOLOGIES_LIST = {
    # ── Cloud Providers ────────────────────────────────────────────────────────
    "AWS", "Amazon Web Services", "Azure", "Microsoft Azure",
    "GCP", "Google Cloud", "Google Cloud Platform",
    "Oracle Cloud", "OCI", "IBM Cloud", "Alibaba Cloud",
    "Cloudflare", "Vercel", "Netlify", "Render", "Railway", "Fly.io",
    "Heroku", "DigitalOcean", "Linode", "Akamai", "Vultr", "Hetzner",

    # ── AWS Services ──────────────────────────────────────────────────────────
    "EC2", "ECS", "EKS", "Fargate", "Lambda", "App Runner",
    "Elastic Beanstalk", "LightSail",
    "S3", "S3 Glacier", "EFS", "FSx",
    "RDS", "Aurora", "DynamoDB", "ElastiCache", "DocumentDB",
    "Neptune", "Timestream", "QLDB", "MemoryDB",
    "Redshift", "EMR", "Glue", "Athena", "Lake Formation",
    "Kinesis", "SQS", "SNS", "EventBridge", "MQ",
    "CloudFront", "Route 53", "VPC", "Direct Connect", "Transit Gateway",
    "ALB", "NLB", "API Gateway", "App Mesh",
    "IAM", "Cognito", "Secrets Manager", "KMS", "WAF", "Shield",
    "GuardDuty", "Inspector", "Macie", "Security Hub",
    "CloudWatch", "CloudTrail", "X-Ray", "Config", "Trusted Advisor",
    "CodeCommit", "CodeBuild", "CodeDeploy", "CodePipeline", "CodeArtifact",
    "CloudFormation", "CDK", "SAM", "Amplify", "AppSync",
    "SageMaker", "Bedrock", "Rekognition", "Textract", "Comprehend",
    "Translate", "Transcribe", "Polly", "Lex",
    "Batch", "Step Functions",
    "ECR", "Elastic Container Registry",
    "OpenSearch Service",
    "MSK", "Managed Kafka",
    "CloudHSM", "ACM",
    "Systems Manager", "SSM", "Parameter Store",
    "Cost Explorer", "Budgets",
    "Organizations", "Control Tower",
    "Global Accelerator", "DataSync",
    "IoT Core", "IoT Greengrass",
    # AWS — Additional services
    "AWS Transfer Family", "AWS DMS", "Database Migration Service",
    "AWS SCT", "Schema Conversion Tool",
    "AWS MGN", "Application Migration Service",
    "AWS Migration Hub",
    "AWS Snow Family", "Snowball", "Snowball Edge", "Snowcone", "Snowmobile",
    "AWS Outposts", "AWS Local Zones",
    "Amazon Connect", "Amazon Chime", "Amazon Pinpoint", "Amazon SES",
    "AWS Firewall Manager", "AWS Network Firewall",
    "AWS Audit Manager", "AWS Artifact",
    "AWS Compute Optimizer", "AWS Health",
    "Amazon Forecast", "Amazon Fraud Detector",
    "Amazon DevOps Guru", "Amazon CodeGuru",
    "Amazon Lookout for Metrics",
    "AWS Amplify Studio", "AWS Device Farm",
    "Amazon Location Service",
    "AWS Elemental", "AWS MediaConvert", "AWS MediaLive",
    "AWS MediaPackage", "Amazon IVS",
    "Amazon Honeycode", "Amazon Managed Blockchain",
    "AWS Nitro", "AWS Nitro System", "AWS Nitro Enclaves",
    "EC2 Image Builder", "AWS Systems Manager Patch Manager",
    "AWS Backup", "AWS Disaster Recovery",
    "AWS Resilience Hub",
    "AWS Well-Architected Tool",
    "AWS Proton", "AWS App2Container",
    "Amazon EKS Anywhere", "Amazon ECS Anywhere",
    "AWS Wavelength", "AWS Ground Station",
    "Amazon Braket",
    "Amazon Managed Grafana", "Amazon Managed Prometheus",
    "AWS Clean Rooms", "Amazon DataZone",
    "AWS Glue DataBrew", "AWS Entity Resolution",
    "Amazon SageMaker Studio", "Amazon SageMaker Canvas",
    "Amazon SageMaker Clarify", "Amazon SageMaker Feature Store",
    "Amazon SageMaker Pipelines", "Amazon SageMaker Model Registry",
    "Amazon Bedrock", "Amazon Titan", "Amazon Nova",
    "Amazon Q", "Amazon Q Developer", "Amazon Q Business",
    "AWS CodeWhisperer",
    "VPC Lattice", "AWS PrivateLink",
    "Amazon VPC", "VPC Flow Logs",
    "AWS Transit Gateway", "AWS Cloud WAN",
    "AWS Resource Access Manager", "AWS RAM",
    "AWS Service Quotas",
    "AWS Launch Wizard", "AWS Marketplace",
    "Amazon WorkSpaces", "Amazon AppStream",
    "AWS End User Computing",

    # ── Azure Services ────────────────────────────────────────────────────────
    "Azure Virtual Machines", "Azure VM", "AKS", "Azure Container Instances",
    "Azure Functions", "Azure App Service", "Azure Container Apps",
    "Azure Static Web Apps", "Azure Kubernetes Service",
    "Azure Blob Storage", "Azure Data Lake", "Azure Files",
    "Azure SQL", "Azure SQL Database", "Azure Cosmos DB",
    "Azure Database for PostgreSQL", "Azure Database for MySQL",
    "Azure Cache for Redis",
    "Azure Synapse Analytics", "Azure Data Factory", "Azure Databricks",
    "Azure Stream Analytics", "Azure Event Hubs", "Azure Service Bus",
    "Azure Event Grid",
    "Azure CDN", "Azure Front Door", "Azure DNS", "Azure Load Balancer",
    "Azure VNet", "Azure ExpressRoute", "Azure Application Gateway",
    "Azure API Management",
    "Azure Active Directory", "Azure AD", "Entra ID",
    "Azure Key Vault", "Azure Defender", "Azure Sentinel",
    "Azure Monitor", "Azure Log Analytics", "Azure Application Insights",
    "Azure DevOps", "Azure Repos", "Azure Pipelines", "Azure Artifacts",
    "ARM Templates", "Bicep",
    "Azure Machine Learning", "Azure Cognitive Services", "Azure OpenAI",
    "Azure Batch", "Azure Logic Apps",
    "Azure Container Registry", "ACR",
    "Azure Notification Hubs", "Azure SignalR",
    "Power Platform", "Power BI", "Power Apps", "Power Automate",

    # ── GCP Services ──────────────────────────────────────────────────────────
    "GKE", "Google Kubernetes Engine", "Cloud Run", "Cloud Functions",
    "Compute Engine", "App Engine", "Cloud Build",
    "Cloud Storage", "Cloud SQL", "Firestore", "Firebase",
    "Cloud Spanner", "Cloud Bigtable", "AlloyDB", "Memorystore",
    "BigQuery", "Dataflow", "Dataproc", "Pub/Sub", "Datastream",
    "Cloud CDN", "Cloud DNS", "Cloud Load Balancing", "Cloud Armor",
    "Identity Platform", "Firebase Auth",
    "Secret Manager", "Cloud KMS",
    "Cloud Monitoring", "Cloud Logging", "Cloud Trace",
    "Cloud Source Repositories", "Cloud Deploy", "Artifact Registry",
    "Vertex AI", "AutoML", "Vision AI",
    "Speech-to-Text", "Text-to-Speech", "Dialogflow",
    "Cloud Composer", "Workflows", "Eventarc",
    "Google Analytics", "Firebase Analytics",
    "Looker", "Looker Studio",

    # ── Containers and Orchestration ──────────────────────────────────────────
    "Docker", "Docker Compose", "Docker Swarm", "Podman", "Buildah",
    "Kubernetes", "K8s", "Helm", "Kustomize", "Skaffold",
    "OpenShift", "Rancher", "Tanzu", "Nomad",
    "containerd", "CRI-O",
    "Knative", "KEDA",
    "Linkerd", "Istio", "Consul Connect",
    "OPA", "Gatekeeper", "Falco",

    # ── CI/CD Platforms ────────────────────────────────────────────────────────
    "Jenkins", "GitHub Actions", "GitLab CI", "GitLab CI/CD",
    "CircleCI", "Travis CI", "TeamCity", "Bamboo", "Buildkite",
    "Drone CI", "Tekton", "Argo Workflows",
    "ArgoCD", "Flux", "FluxCD", "Spinnaker", "Harness", "Octopus Deploy",
    "Azure Pipelines", "Azure DevOps",
    "Bitbucket Pipelines", "Semaphore CI", "Codefresh",

    # ── Relational Databases ──────────────────────────────────────────────────
    "PostgreSQL", "Postgres", "MySQL", "MariaDB", "SQLite", "Oracle",
    "Oracle Database", "MS SQL Server", "SQL Server", "Microsoft SQL Server",
    "IBM Db2", "SAP HANA", "Teradata",
    "CockroachDB", "YugabyteDB", "SingleStore", "PlanetScale", "Neon",
    "Supabase", "TimescaleDB",

    # ── NoSQL Databases ───────────────────────────────────────────────────────
    "MongoDB", "CouchDB", "Couchbase", "ArangoDB",
    "Cassandra", "Apache Cassandra", "ScyllaDB", "HBase",
    "Redis", "KeyDB", "Dragonfly",
    "DynamoDB", "FaunaDB",
    "Elasticsearch", "OpenSearch", "Solr", "MeiliSearch", "Typesense",
    "Algolia",
    "Neo4j", "Amazon Neptune",
    "InfluxDB", "VictoriaMetrics",
    "Firebase Realtime Database", "Firestore",
    "LevelDB", "RocksDB",

    # ── Data Warehouses / OLAP ────────────────────────────────────────────────
    "Snowflake", "BigQuery", "Redshift", "Azure Synapse", "Databricks",
    "ClickHouse", "Druid", "Pinot", "Greenplum",
    "Vertica", "DuckDB", "Starburst", "Trino", "Presto",

    # ── Message Queues / Streaming ────────────────────────────────────────────
    "Apache Kafka", "Kafka", "Confluent Kafka",
    "RabbitMQ", "ActiveMQ",
    "NATS", "NATS JetStream", "ZeroMQ",
    "Apache Pulsar", "Pulsar", "Redpanda",
    "Celery", "Sidekiq", "Bull", "BullMQ",
    "Temporal", "Apache Camel",

    # ── Monitoring / Logging / Observability ──────────────────────────────────
    "Prometheus", "Grafana", "Grafana Loki", "Grafana Tempo",
    "Datadog", "New Relic", "Dynatrace", "AppDynamics",
    "Splunk", "Sumo Logic",
    "ELK Stack", "Logstash", "Kibana", "Beats", "Filebeat",
    "OpenTelemetry", "Jaeger", "Zipkin", "Honeycomb",
    "Sentry", "Rollbar", "Bugsnag",
    "PagerDuty", "OpsGenie", "Alertmanager",
    "CloudWatch", "Azure Monitor", "Google Cloud Monitoring",
    "Nagios", "Zabbix", "Netdata",

    # ── Infrastructure as Code ────────────────────────────────────────────────
    "Terraform", "OpenTofu", "Pulumi", "AWS CDK", "AWS SAM",
    "CloudFormation", "ARM Templates", "Bicep",
    "Ansible", "Puppet", "Chef", "SaltStack",
    "Packer", "Vagrant", "Crossplane",
    "Terragrunt", "Atlantis",

    # ── Service Mesh / API Gateway / Networking ───────────────────────────────
    "Istio", "Linkerd", "Consul", "Envoy", "Traefik", "Nginx", "HAProxy", "Caddy",
    "Kong", "Kong Gateway", "AWS API Gateway",
    "Azure API Management", "Apigee",
    "Cloudflare Workers", "Fastly",

    # ── Security Platforms ────────────────────────────────────────────────────
    "HashiCorp Vault", "Vault", "AWS Secrets Manager", "Azure Key Vault",
    "Google Secret Manager",
    "Okta", "Auth0", "Keycloak", "FusionAuth", "Ping Identity",
    "CrowdStrike", "Carbon Black", "SentinelOne",
    "Snyk", "Aqua Security",
    "OWASP ZAP", "Burp Suite", "Nessus", "Qualys",
    "Trivy", "Grype",
    "AWS Security Hub", "AWS GuardDuty", "Azure Defender",

    # ── Storage Services ──────────────────────────────────────────────────────
    "S3", "Azure Blob Storage", "Google Cloud Storage", "GCS",
    "MinIO", "Ceph", "HDFS",
    "Backblaze B2",

    # ── CDN / Edge ────────────────────────────────────────────────────────────
    "CloudFront", "Cloudflare CDN", "Fastly", "Akamai",
    "Azure CDN", "Google Cloud CDN",
    "Vercel Edge", "Netlify Edge Functions",

    # ── Data Pipeline / ETL / ELT ─────────────────────────────────────────────
    "Fivetran", "Airbyte", "Stitch", "Talend", "Informatica",
    "dbt", "dbt Cloud", "dbt Core",
    "Apache Airflow", "Airflow", "Prefect", "Dagster", "Mage",
    "Azure Data Factory", "AWS Glue", "Google Dataflow",
    "Kafka Streams", "ksqlDB",

    # ── Communication / Collaboration ─────────────────────────────────────────
    "Slack", "Microsoft Teams", "Discord", "Google Chat",
    "Zoom", "Webex", "Google Meet",
    "Confluence", "Notion", "GitBook",
    "Jira", "Linear", "Trello", "Asana", "Monday.com",
    "ClickUp", "Basecamp", "YouTrack",
    "GitHub Issues", "GitLab Issues",
    "Figma", "Miro", "Mural", "Lucidchart",
    "PagerDuty", "OpsGenie",

    # ── IDEs and Development Environments ─────────────────────────────────────
    "VS Code", "Visual Studio Code", "Visual Studio",
    "IntelliJ IDEA", "IntelliJ", "PyCharm", "WebStorm",
    "GoLand", "RubyMine", "Rider", "CLion", "DataGrip",
    "PhpStorm", "Android Studio",
    "Vim", "Neovim", "Emacs",
    "Eclipse", "NetBeans", "Sublime Text",
    "Xcode", "Cursor",
    "Jupyter", "RStudio",
    "GitHub Codespaces", "Gitpod", "Replit",

    # ── Testing / Quality Platforms ────────────────────────────────────────────
    "SonarQube", "SonarCloud", "CodeClimate", "Coverity",
    "Checkmarx", "Veracode", "Fortify",
    "Browserstack", "Sauce Labs", "LambdaTest",
    "TestRail", "Xray", "Zephyr",
    "LaunchDarkly", "Split.io", "Unleash",

    # ── Analytics / BI ────────────────────────────────────────────────────────
    "Tableau", "Power BI", "Looker", "Metabase", "Redash",
    "Apache Superset", "Mode Analytics", "Hex",
    "Google Analytics", "Mixpanel", "Amplitude", "Segment",
    "Heap", "FullStory", "Hotjar", "Pendo",

    # ── AI / ML Platforms ─────────────────────────────────────────────────────
    "OpenAI API", "Anthropic", "Cohere", "Ollama",
    "Hugging Face Hub", "Replicate",
    "AWS SageMaker", "Azure Machine Learning", "Vertex AI",
    "MLflow", "Weights & Biases",
    "Pinecone", "Weaviate", "Qdrant", "Chroma",

    # ── VCS Hosting / Artifact Registries ────────────────────────────────────
    "GitHub", "GitLab", "Bitbucket", "Azure Repos",
    "Docker Hub", "JFrog Artifactory", "Nexus Repository",
    "GitHub Packages", "GitLab Container Registry", "ECR", "ACR",

    # ── Operating Systems / Infrastructure ────────────────────────────────────
    "Linux", "Ubuntu", "Debian", "CentOS", "RHEL", "Fedora",
    "Alpine Linux", "Windows Server",
    "VMware", "vSphere", "ESXi", "Hyper-V", "KVM",
    "Proxmox",
    "Ansible Tower", "AWX",
    "Tailscale", "WireGuard", "OpenVPN",
    "Let's Encrypt", "Certbot",
}


SOFT_SKILLS_LIST = {
    # ── Communication ─────────────────────────────────────────────────────────
    "communication", "written communication", "verbal communication",
    "technical communication", "effective communication",
    "active listening", "listening skills",
    "presentation skills", "public speaking", "storytelling",
    "technical writing", "documentation skills", "writing skills",
    "proposal writing", "report writing", "business writing",
    "cross-functional communication", "asynchronous communication",
    "meeting facilitation", "facilitating discussions",

    # ── Leadership ────────────────────────────────────────────────────────────
    "leadership", "technical leadership", "thought leadership",
    "engineering leadership", "team leadership", "project leadership",
    "servant leadership",
    "people management", "team management",
    "managing distributed teams", "managing remote teams",
    "leading cross-functional teams",
    "influence without authority", "driving alignment",
    "decision making", "decision-making", "sound judgment",
    "executive presence", "strategic leadership",
    "change leadership", "leading through ambiguity",
    "hiring", "recruiting",
    "performance management", "performance reviews",
    "giving feedback", "receiving feedback", "constructive feedback",
    "radical candor",

    # ── Team Collaboration ────────────────────────────────────────────────────
    "teamwork", "collaboration", "team collaboration",
    "cross-functional collaboration", "cross-team collaboration",
    "building relationships", "relationship building",
    "partnership", "working with stakeholders",
    "team player", "collaborative",
    "remote team collaboration",

    # ── Customer / Client Skills ──────────────────────────────────────────────
    "customer focus", "customer-centric", "customer empathy",
    "customer service", "client management", "client relations",
    "client communication", "stakeholder communication",
    "managing expectations", "expectation setting",
    "user empathy", "user advocacy", "user research",
    "gathering requirements", "requirements elicitation",
    "discovery", "needs analysis", "business analysis",
    "account management", "vendor management",

    # ── Project Management ────────────────────────────────────────────────────
    "project management", "program management", "portfolio management",
    "delivery management", "milestone management", "scope management",
    "project planning", "workback planning", "scheduling",
    "resource management", "capacity planning",
    "risk management", "risk identification", "risk mitigation",
    "dependency management",
    "status reporting", "project status updates",
    "budget management", "budget tracking",
    "sprint planning", "backlog grooming", "backlog refinement",
    "release management", "release planning",
    "agile project management", "scrum master",

    # ── Problem Solving / Analytical ──────────────────────────────────────────
    "problem solving", "problem-solving", "complex problem solving",
    "analytical thinking", "analytical skills",
    "critical thinking", "systems thinking",
    "root cause analysis", "RCA", "troubleshooting",
    "data-driven decision making", "data-driven",
    "structured thinking", "first principles thinking",
    "creative problem solving", "innovative thinking",
    "logical reasoning", "hypothesis-driven",
    "quantitative analysis", "qualitative analysis",

    # ── Organizational / Planning Skills ──────────────────────────────────────
    "organization", "organizational skills",
    "time management", "managing time effectively",
    "prioritization", "priority management",
    "planning", "strategic planning", "operational planning",
    "goal setting", "OKRs",
    "execution", "bias for action",
    "multitasking", "managing multiple priorities",
    "attention to detail", "detail-oriented", "thoroughness",
    "process improvement", "process documentation",
    "workflow optimization",
    "deadline management", "deadline-driven", "delivering on time",
    "follow-through", "follow-up",

    # ── Teaching / Mentoring ──────────────────────────────────────────────────
    "mentoring", "mentorship", "coaching", "teaching",
    "mentoring junior developers", "guiding junior engineers",
    "technical mentorship", "knowledge sharing", "knowledge transfer",
    "onboarding", "onboarding new hires",
    "pair programming", "mob programming", "code review",
    "writing documentation", "creating learning materials",
    "workshop facilitation", "training delivery",
    "blogging", "conference speaking",

    # ── Agile / Process Skills ────────────────────────────────────────────────
    "agile", "agile methodology", "agile development",
    "scrum", "scrum ceremonies", "sprint retrospectives",
    "kanban", "lean", "lean methodology",
    "iterative development", "incremental delivery",
    "continuous improvement", "kaizen",
    "retrospectives", "blameless post-mortems", "post-mortems",
    "standups", "daily standups",
    "estimation", "story points", "planning poker",
    "velocity tracking",

    # ── Business Skills ────────────────────────────────────────────────────────
    "business acumen", "business understanding", "business analysis",
    "understanding business requirements", "translating business requirements",
    "requirements gathering", "requirements analysis",
    "stakeholder management", "managing stakeholders",
    "executive communication", "C-suite communication",
    "product sense", "product thinking", "product mindset",
    "roadmap planning", "roadmapping",
    "go-to-market", "launch strategy",
    "market awareness", "competitive analysis",
    "cost-benefit analysis", "trade-off analysis",
    "ROI analysis", "business case development",
    "negotiation", "contract negotiation", "vendor negotiation",

    # ── Personal Effectiveness ────────────────────────────────────────────────
    "self-motivated", "self-starter", "self-directed",
    "proactive", "initiative", "taking initiative",
    "ownership", "taking ownership", "accountability",
    "reliability", "dependability",
    "integrity", "transparency",
    "growth mindset", "continuous learning", "learning agility",
    "intellectual curiosity", "curiosity", "desire to learn",
    "adaptability", "adaptable", "flexibility", "flexible",
    "resilience", "working under pressure",
    "ambiguity tolerance", "working with ambiguity",
    "work ethic", "hardworking",
    "results-oriented", "results-driven", "outcome-focused",
    "deep work", "focus",
    "autonomy", "independent worker", "works independently",
    "entrepreneurial", "entrepreneurial mindset",
    "bias for action",
    "creative", "creativity", "innovation", "innovative",

    # ── Emotional Intelligence ────────────────────────────────────────────────
    "emotional intelligence", "self-awareness",
    "empathy", "empathetic", "compassion",
    "social awareness", "relationship management",
    "conflict resolution", "conflict management",
    "managing difficult conversations",
    "psychological safety", "creating psychological safety",
    "patience", "composure",
    "humility", "intellectual humility",
    "open-mindedness", "open to feedback",
    "cultural sensitivity", "cultural awareness",

    # ── Diversity, Equity, and Inclusion ─────────────────────────────────────
    "diversity and inclusion", "DEI", "inclusive leadership",
    "equity", "belonging",
    "allyship", "bias awareness",
    "inclusive communication", "inclusive design",
    "accessibility advocacy",
    "cross-cultural communication", "global mindset",
    "multicultural teams", "working across cultures",

    # ── Influence and Persuasion ──────────────────────────────────────────────
    "persuasion", "persuasive communication", "influencing others",
    "consensus building", "building consensus",
    "driving alignment", "alignment across teams",
    "navigating competing priorities",
    "selling ideas", "pitching",
    "advocacy", "championing initiatives",

    # ── Strategy and Vision ────────────────────────────────────────────────────
    "strategic thinking", "big picture thinking",
    "long-term planning", "vision setting", "defining vision",
    "technical strategy", "engineering strategy",
    "architecture decision-making", "technical direction",
    "balancing short-term and long-term", "thinking at scale",

    # ── Professional Skills ────────────────────────────────────────────────────
    "fast learner", "quick learner",
    "customer obsession", "user obsession",
    "shipping", "shipping quickly",
    "pragmatism", "pragmatic",
    "quality mindset", "security mindset",
    "documentation culture",
    "frugality", "cost consciousness",
    "incident response", "being on-call",
    "postmortem culture", "learning from failures",
    "cross-cultural", "interpersonal", "interpersonal skills",
    "facilitation", "coordination",
}

EMPTY_RESULT = {
    "skills": [],
    "technologies": [],
    "soft_skills": [],
}


# ── SpaCy pipeline ────────────────────────────────────────────────────────────

import spacy
from spacy.matcher import PhraseMatcher

_nlp = None
_skills_matcher: PhraseMatcher | None = None
_tech_matcher: PhraseMatcher | None = None
_soft_matcher: PhraseMatcher | None = None

# Maps canonical-lowercase → canonical-cased term for all three lists
_skills_lower: dict[str, str] = {t.lower(): t for t in SKILLS_LIST}
_tech_lower: dict[str, str] = {t.lower(): t for t in TECHNOLOGIES_LIST}
_soft_lower: dict[str, str] = {t.lower(): t for t in SOFT_SKILLS_LIST}


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm", disable=["ner"])
    return _nlp


def _build_matcher(word_list: set[str], label: str) -> PhraseMatcher:
    nlp = _get_nlp()
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    patterns = [nlp.make_doc(term.lower()) for term in word_list]
    matcher.add(label, patterns)
    return matcher


def _get_skills_matcher() -> PhraseMatcher:
    global _skills_matcher
    if _skills_matcher is None:
        _skills_matcher = _build_matcher(SKILLS_LIST, "SKILL")
    return _skills_matcher


def _get_tech_matcher() -> PhraseMatcher:
    global _tech_matcher
    if _tech_matcher is None:
        _tech_matcher = _build_matcher(TECHNOLOGIES_LIST, "TECH")
    return _tech_matcher


def _get_soft_matcher() -> PhraseMatcher:
    global _soft_matcher
    if _soft_matcher is None:
        _soft_matcher = _build_matcher(SOFT_SKILLS_LIST, "SOFT")
    return _soft_matcher


def _run_matcher(text: str, matcher: PhraseMatcher, lower_map: dict[str, str]) -> list[str]:
    nlp = _get_nlp()
    doc = nlp(text)
    found: set[str] = set()
    for _match_id, start, end in matcher(doc):
        span_lower = doc[start:end].text.lower()
        canonical = lower_map.get(span_lower)
        if canonical:
            found.add(canonical)
    return sorted(found)


# ── Public API ─────────────────────────────────────────────────────────────────

def extract_skills(text: str) -> list[str]:
    """Return programming languages, frameworks, and dev tools found in text."""
    if not text or not text.strip():
        return []
    return _run_matcher(text, _get_skills_matcher(), _skills_lower)


def extract_technologies(text: str) -> list[str]:
    """Return infrastructure, platforms, databases, and cloud services found in text."""
    if not text or not text.strip():
        return []
    return _run_matcher(text, _get_tech_matcher(), _tech_lower)


def extract_soft_skills(text: str) -> list[str]:
    """Return soft skills found in text."""
    if not text or not text.strip():
        return []
    return _run_matcher(text, _get_soft_matcher(), _soft_lower)


def extract_from_documents(doc_contents: str) -> dict:
    """
    Main entry point. Returns {"skills", "technologies", "soft_skills"}.
    Works completely offline via spaCy — no API calls made.
    """
    if doc_contents == "No previewable documents found.":
        return dict(EMPTY_RESULT)

    return {
        "skills": extract_skills(doc_contents),
        "technologies": extract_technologies(doc_contents),
        "soft_skills": extract_soft_skills(doc_contents),
    }
