# Certificate Models Documentation

## Overview

The Certificate Tracking System uses three main models to track employee certifications:

1. **CertificateProvider** - Organizations that issue certificates (CompTIA, Microsoft, AWS, etc.)
2. **CertificateCategory** - Categories for organizing certificates (Security, Cloud, Networking, etc.)
3. **Certificate** - Main model tracking individual employee certifications

## Database Schema

```
┌─────────────────────────┐
│  CertificateProvider    │
├─────────────────────────┤
│ id (PK)                 │
│ name (UNIQUE)           │
│ website                 │
│ description             │
│ logo                    │
│ is_active               │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
         ▲
         │ provider_id (FK)
         │
         │
┌─────────────────────────┐        ┌─────────────────────────┐
│  Certificate            │        │  CertificateCategory    │
├─────────────────────────┤        ├─────────────────────────┤
│ id (PK)                 │        │ id (PK)                 │
│ user_id (FK)           ─┼───────>│ name (UNIQUE)           │
│ provider_id (FK)       ─┘        │ description             │
│ category_id (FK)       ─────────>│ icon_class              │
│ name                    │        │ color                   │
│ certification_id        │        │ created_at              │
│ issue_date              │        │ updated_at              │
│ expiry_date             │        └─────────────────────────┘
│ status                  │
│ certificate_file        │
│ verification_url        │
│ notes                   │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
         │
         │ user_id (FK)
         ▼
┌─────────────────────────┐
│  User                   │
│  (from accounts app)    │
└─────────────────────────┘
```

## Model 1: CertificateProvider

### Purpose
Stores information about organizations that issue certifications.

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | BigAutoField | Primary Key | Auto-incrementing ID |
| `name` | CharField(100) | **Unique**, Required | Provider name (e.g., "CompTIA", "Microsoft") |
| `website` | URLField | Optional | Official provider website |
| `description` | TextField | Optional | What this provider specializes in |
| `logo` | ImageField | Optional | Provider logo (uploads to `media/providers/YYYY/MM/`) |
| `is_active` | BooleanField | Default: True | Soft delete flag |
| `created_at` | DateTimeField | Auto-set | When record was created |
| `updated_at` | DateTimeField | Auto-update | When record was last modified |

### Relationships
- **One-to-Many** with Certificate: One provider can issue many certificates
- Uses `PROTECT` delete behavior: Cannot delete provider if certificates exist

### Indexes
- `name` - Fast provider lookups
- `is_active` - Filter active providers

### Methods

```python
def get_certificate_count():
    """Returns total number of certificates from this provider"""

def get_active_certificate_count():
    """Returns number of active certificates from this provider"""
```

### Example Usage

```python
# Create a provider
comptia = CertificateProvider.objects.create(
    name='CompTIA',
    website='https://www.comptia.org',
    description='Leading provider of IT certifications',
    is_active=True
)

# Get all providers
providers = CertificateProvider.objects.filter(is_active=True)

# Get provider with certificate count
provider = CertificateProvider.objects.get(name='CompTIA')
total_certs = provider.get_certificate_count()
active_certs = provider.get_active_certificate_count()
```

## Model 2: CertificateCategory

### Purpose
Organizes certificates into categories for filtering and reporting.

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | BigAutoField | Primary Key | Auto-incrementing ID |
| `name` | CharField(100) | **Unique**, Required | Category name (e.g., "Security") |
| `description` | TextField | Optional | What types of certs belong here |
| `icon_class` | CharField(50) | Optional | CSS icon class (e.g., "fa-shield") |
| `color` | CharField(7) | Default: "#3B82F6" | Hex color code for UI theming |
| `created_at` | DateTimeField | Auto-set | When record was created |
| `updated_at` | DateTimeField | Auto-update | When record was last modified |

### Relationships
- **One-to-Many** with Certificate: One category can contain many certificates
- Uses `PROTECT` delete behavior: Cannot delete category if certificates exist

### Indexes
- `name` - Fast category lookups

### Methods

```python
def get_certificate_count():
    """Returns total number of certificates in this category"""

def get_active_certificate_count():
    """Returns number of active certificates in this category"""
```

### Example Usage

```python
# Create categories
security = CertificateCategory.objects.create(
    name='Security',
    description='Cybersecurity certifications',
    icon_class='fa-shield',
    color='#F87272'  # Red
)

cloud = CertificateCategory.objects.create(
    name='Cloud Computing',
    description='Cloud platform certifications',
    icon_class='fa-cloud',
    color='#3B82F6'  # Blue
)

# Get all categories
categories = CertificateCategory.objects.all()

# Get category with stats
category = CertificateCategory.objects.get(name='Security')
total = category.get_certificate_count()
active = category.get_active_certificate_count()
```

## Model 3: Certificate

### Purpose
Main model tracking individual employee certifications.

### Fields

| Field | Type | Constraints | Description |
|-------|------|------------|-------------|
| `id` | BigAutoField | Primary Key | Auto-incrementing ID |
| `user` | ForeignKey(User) | **Required**, CASCADE | Employee who owns this certificate |
| `provider` | ForeignKey(Provider) | **Required**, PROTECT | Organization that issued it |
| `category` | ForeignKey(Category) | **Required**, PROTECT | Category it belongs to |
| `name` | CharField(200) | **Required** | Full certificate name |
| `certification_id` | CharField(100) | Optional | Credential ID from provider |
| `issue_date` | DateField | **Required** | When certificate was issued |
| `expiry_date` | DateField | Optional | When it expires (null = lifetime) |
| `status` | CharField(10) | Default: ACTIVE | ACTIVE, EXPIRED, or REVOKED |
| `certificate_file` | FileField | Optional | PDF/image of certificate |
| `verification_url` | URLField | Optional | Online verification link |
| `notes` | TextField | Optional | Additional notes |
| `created_at` | DateTimeField | Auto-set | When record was created |
| `updated_at` | DateTimeField | Auto-update | When record was last modified |

### Status Choices

```python
STATUS_CHOICES = [
    ('ACTIVE', 'Active'),     # Certificate is valid
    ('EXPIRED', 'Expired'),   # Certificate has expired
    ('REVOKED', 'Revoked'),   # Certificate was revoked
]
```

### Relationships

- **Many-to-One** with User: User can have many certificates
  - Delete behavior: `CASCADE` - Deleting user deletes their certificates

- **Many-to-One** with CertificateProvider: Provider can issue many certificates
  - Delete behavior: `PROTECT` - Cannot delete provider if certificates exist

- **Many-to-One** with CertificateCategory: Category can contain many certificates
  - Delete behavior: `PROTECT` - Cannot delete category if certificates exist

### Indexes

For performance optimization:

1. `(user, status)` - Filter certificates by user and status
2. `provider` - Group certificates by provider
3. `category` - Group certificates by category
4. `status` - Filter by status
5. `expiry_date` - Sort/filter by expiry
6. `-issue_date` - Sort by issue date (newest first)

### Methods

#### `is_expired()` → bool
Check if certificate has expired.

```python
cert = Certificate.objects.get(id=1)
if cert.is_expired():
    print("Certificate is expired!")

# Logic:
# - No expiry_date → False (lifetime cert)
# - expiry_date in past → True
# - expiry_date in future → False
```

#### `days_until_expiry()` → int | None
Calculate days remaining until expiry.

```python
cert = Certificate.objects.get(id=1)
days_left = cert.days_until_expiry()

if days_left is None:
    print("Lifetime certification")
elif days_left < 0:
    print(f"Expired {abs(days_left)} days ago")
elif days_left == 0:
    print("Expires today!")
elif days_left <= 90:
    print(f"Expiring soon: {days_left} days")
else:
    print(f"Valid for {days_left} days")
```

Returns:
- `int` - Days until expiry (negative if already expired)
- `None` - No expiry date (lifetime certification)

#### `is_expiring_soon(days_threshold=90)` → bool
Check if certificate is expiring within specified threshold.

```python
# Check if expiring within 90 days (default)
if cert.is_expiring_soon():
    send_renewal_reminder(cert)

# Check if expiring within 30 days
if cert.is_expiring_soon(30):
    send_urgent_reminder(cert)
```

#### `get_status_display_class()` → str
Get DaisyUI badge class for status display.

```python
cert = Certificate.objects.get(id=1)
badge_class = cert.get_status_display_class()
# Returns: 'badge-success', 'badge-error', or 'badge-warning'
```

Mapping:
- `ACTIVE` → `badge-success` (green)
- `EXPIRED` → `badge-error` (red)
- `REVOKED` → `badge-warning` (yellow)

#### `get_expiry_status_class()` → str
Get DaisyUI badge class based on expiry status.

```python
cert = Certificate.objects.get(id=1)
badge_class = cert.get_expiry_status_class()
```

Returns:
- `badge-info` - No expiry (lifetime)
- `badge-error` - Expired
- `badge-warning` - Expiring soon (< 90 days)
- `badge-success` - Valid (> 90 days)

#### `auto_update_status()`
Automatically update status based on expiry date.

```python
# Update single certificate
cert.auto_update_status()

# Update all certificates (e.g., daily cron job)
for cert in Certificate.objects.filter(status='ACTIVE'):
    cert.auto_update_status()
```

Logic:
- If `status='ACTIVE'` and `is_expired()` → changes to `EXPIRED`
- Does NOT change `REVOKED` status

#### `save()`
Overridden to auto-update status on save.

```python
# Status is automatically updated when saving
cert = Certificate.objects.get(id=1)
cert.expiry_date = timezone.now().date() - timedelta(days=1)
cert.save()  # Automatically sets status='EXPIRED'
```

#### `get_absolute_url()` → str
Get URL for certificate detail view.

```python
cert = Certificate.objects.get(id=1)
url = cert.get_absolute_url()
# Returns: '/certificates/detail/1/'
```

### Example Usage

```python
from django.utils import timezone
from datetime import timedelta
from accounts.models import User
from certificates.models import Certificate, CertificateProvider, CertificateCategory

# Get user
user = User.objects.get(email='employee@example.com')

# Get or create provider and category
comptia = CertificateProvider.objects.get(name='CompTIA')
security = CertificateCategory.objects.get(name='Security')

# Create certificate
cert = Certificate.objects.create(
    user=user,
    provider=comptia,
    category=security,
    name='CompTIA Security+ CE',
    certification_id='COMP001234567',
    issue_date=timezone.now().date() - timedelta(days=365),
    expiry_date=timezone.now().date() + timedelta(days=730),
    status='ACTIVE',
    verification_url='https://www.comptia.org/verify',
    notes='Renew every 3 years with 50 CEUs'
)

# Check expiry
if cert.is_expiring_soon(90):
    print(f"Certificate expiring in {cert.days_until_expiry()} days")

# Filter certificates
active_certs = Certificate.objects.filter(status='ACTIVE')
expired_certs = Certificate.objects.filter(status='EXPIRED')
user_certs = Certificate.objects.filter(user=user)

# Expiring soon (next 90 days)
expiring_soon = []
for cert in Certificate.objects.filter(status='ACTIVE'):
    if cert.is_expiring_soon(90):
        expiring_soon.append(cert)

# Update expired certificates
Certificate.objects.filter(status='ACTIVE').update()
for cert in Certificate.objects.filter(status='ACTIVE'):
    cert.auto_update_status()
```

## Migration Explained: 0001_initial.py

### What This Migration Does

The migration creates three database tables:

#### 1. `certificates_certificatecategory`
```sql
CREATE TABLE certificates_certificatecategory (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon_class VARCHAR(50),
    color VARCHAR(7) DEFAULT '#3B82F6',
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX certificate_name_37004a_idx ON certificates_certificatecategory (name);
```

#### 2. `certificates_certificateprovider`
```sql
CREATE TABLE certificates_certificateprovider (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    website VARCHAR(200),
    description TEXT,
    logo VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL
);

CREATE INDEX certificate_name_7fcfb0_idx ON certificates_certificateprovider (name);
CREATE INDEX certificate_is_acti_7fb840_idx ON certificates_certificateprovider (is_active);
```

#### 3. `certificates_certificate`
```sql
CREATE TABLE certificates_certificate (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    certification_id VARCHAR(100),
    issue_date DATE NOT NULL,
    expiry_date DATE,
    status VARCHAR(10) DEFAULT 'ACTIVE',
    certificate_file VARCHAR(100),
    verification_url VARCHAR(200),
    notes TEXT,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    user_id BIGINT NOT NULL FOREIGN KEY REFERENCES accounts_user(id) ON DELETE CASCADE,
    category_id BIGINT NOT NULL FOREIGN KEY REFERENCES certificates_certificatecategory(id) ON DELETE PROTECT,
    provider_id BIGINT NOT NULL FOREIGN KEY REFERENCES certificates_certificateprovider(id) ON DELETE PROTECT
);

-- Indexes for performance
CREATE INDEX certificate_user_id_42f10a_idx ON certificates_certificate (user_id, status);
CREATE INDEX certificate_provide_8e16c5_idx ON certificates_certificate (provider_id);
CREATE INDEX certificate_categor_6654e9_idx ON certificates_certificate (category_id);
CREATE INDEX certificate_status_31e804_idx ON certificates_certificate (status);
CREATE INDEX certificate_expiry__2f5bd0_idx ON certificates_certificate (expiry_date);
CREATE INDEX certificate_issue_d_b2f3d3_idx ON certificates_certificate (issue_date DESC);
```

### Foreign Key Relationships Explained

#### user_id → accounts_user (CASCADE)
```python
on_delete=models.CASCADE
```
**Meaning**: When a User is deleted, **all** their certificates are automatically deleted.

**Why CASCADE?**
- Certificates belong to users
- No orphaned certificates without an owner
- Maintains data integrity

**Example**:
```python
user = User.objects.get(email='employee@example.com')
user.delete()
# All certificates for this user are automatically deleted
```

#### provider_id → certificateprovider (PROTECT)
```python
on_delete=models.PROTECT
```
**Meaning**: Cannot delete a provider if certificates reference it.

**Why PROTECT?**
- Prevents accidental data loss
- Maintains historical records
- Forces explicit handling of certificates before provider deletion

**Example**:
```python
comptia = CertificateProvider.objects.get(name='CompTIA')
comptia.delete()
# Raises ProtectedError: Cannot delete provider with existing certificates

# Must first:
# 1. Reassign certificates to another provider, OR
# 2. Delete all certificates from this provider, OR
# 3. Mark provider as inactive instead: comptia.is_active = False
```

#### category_id → certificatecategory (PROTECT)
```python
on_delete=models.PROTECT
```
**Meaning**: Cannot delete a category if certificates reference it.

**Why PROTECT?**
- Same reasons as provider
- Prevents categorization data loss
- Requires explicit recategorization

### Index Strategy

**Why these indexes?**

1. **`(user_id, status)`** - Composite index
   - Query: "Show me all ACTIVE certificates for user X"
   - Most common query pattern
   - Covers both user filtering and status filtering

2. **`provider_id`** - Foreign key index
   - Query: "Show all certificates from CompTIA"
   - Dashboard statistics by provider

3. **`category_id`** - Foreign key index
   - Query: "Show all Security certificates"
   - Dashboard statistics by category

4. **`status`** - Single column index
   - Query: "Show all EXPIRED certificates"
   - Admin bulk operations

5. **`expiry_date`** - Single column index
   - Query: "Show certificates expiring in next 90 days"
   - Renewal reminders

6. **`-issue_date`** - Descending index
   - Query: "Show newest certificates first"
   - Default ordering

## Best Practices

### 1. Always Set Expiry Date (If Applicable)
```python
# ✅ Good - Set expiry for renewable certs
cert = Certificate.objects.create(
    ...
    expiry_date=timezone.now().date() + timedelta(days=1095)  # 3 years
)

# ✅ Good - No expiry for lifetime certs
cert = Certificate.objects.create(
    ...
    expiry_date=None  # Lifetime certification
)

# ❌ Bad - Leaving it ambiguous
cert = Certificate.objects.create(
    ...
    # Should this expire or not?
)
```

### 2. Use Auto-Update Status
```python
# ✅ Good - Automatic status updates
cert.save()  # Status automatically updated if expired

# ✅ Good - Batch update via cron job
for cert in Certificate.objects.filter(status='ACTIVE'):
    cert.auto_update_status()

# ❌ Bad - Manual status tracking (can get out of sync)
if cert.expiry_date < timezone.now().date():
    cert.status = 'EXPIRED'
    cert.save()
```

### 3. Provide Verification URL When Possible
```python
# ✅ Good - Provides verification
cert = Certificate.objects.create(
    ...
    verification_url='https://www.comptia.org/verify',
    certification_id='COMP001234567'
)

# This allows:
# - Verification by third parties
# - Audit compliance
# - Trust verification
```

### 4. Use PROTECT Wisely
```python
# ✅ Good - Mark as inactive instead of deleting
provider = CertificateProvider.objects.get(name='OldProvider')
provider.is_active = False
provider.save()

# ✅ Good - Reassign before deleting
old_provider = CertificateProvider.objects.get(name='Old')
new_provider = CertificateProvider.objects.get(name='New')
Certificate.objects.filter(provider=old_provider).update(provider=new_provider)
old_provider.delete()  # Now safe to delete

# ❌ Bad - Trying to delete without handling certificates
provider.delete()  # Raises ProtectedError
```

### 5. Leverage Querysets Efficiently
```python
# ✅ Good - Filter at database level
expiring = Certificate.objects.filter(
    status='ACTIVE',
    expiry_date__lte=timezone.now().date() + timedelta(days=90)
)

# ❌ Bad - Filter in Python (loads all records)
all_certs = Certificate.objects.all()
expiring = [c for c in all_certs if c.is_expiring_soon()]
```

## Summary

The certificate models provide:

✅ **Complete certificate tracking** - Provider, category, dates, status
✅ **Automatic expiry management** - Auto-update status based on dates
✅ **Flexible organization** - Categories and providers
✅ **File uploads** - Store certificate PDFs/images
✅ **Audit trail** - Created/updated timestamps
✅ **Performance optimized** - Strategic indexes
✅ **Data integrity** - Protected foreign keys
✅ **Business logic** - Expiry calculations, status badges
✅ **Admin interface** - Comprehensive Django admin

Next steps:
- **Step 7**: Create CRUD views for certificates
- **Step 8**: Employee profile pages with certificate lists
- **Step 9**: Dashboard with certificate statistics
- **Step 10**: DataTables for certificate management
