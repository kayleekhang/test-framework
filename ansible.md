```
integration-framework/
├── deployment/
│   ├── inventory/
│   │   ├── dev.ini
│   │   └── vehicle_system.ini
│   │
│   ├── playbooks/
│   │   ├── deploy_system.yml
│   │   ├── start_system.yml
│   │   ├── stop_system.yml
│   │   └── clean_system.yml
│   │
│   ├── roles/
│   │   ├── common/
│   │   │   └── tasks/
│   │   │       └── main.yml
│   │   │
│   │   ├── product_deploy/
│   │   │   ├── tasks/
│   │   │   │   └── main.yml
│   │   │   ├── templates/
│   │   │   │   └── product.service.j2
│   │   │   └── defaults/
│   │   │       └── main.yml
│   │   │
│   │   └── system_control/
│   │       └── tasks/
│   │           └── main.yml
│   │
│   └── group_vars/
│       └── vehicle_system.yml
```
