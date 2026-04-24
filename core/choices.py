from django.db import models

class ProjectStatusChoices(models.IntegerChoices):
    ACTIVE = 0, 'Active'         
    DEACTIVE = 1, 'DeActive' 


class SubmissionStatusChoices(models.IntegerChoices):
    NOTSUBMITTED = 0, "Not Submitted"
    APPROVED = 1, "Approved"
    REJECTED = 2, "Rejected"
    SUBMITTED = 3, "Submitted"


class DataOriginChoices(models.IntegerChoices):
    PUBLIC = 0, "Public"
    PRIVATE = 1, "Private"
    MIXED = 2, "Mixed"


class GovernanceStatusChoices(models.IntegerChoices):
    APPROVED = 0, "Approved"
    PENDING = 1, "Pending"
    FLAGGED = 2, "Flagged"


class RecordOriginChoices(models.IntegerChoices):
    MANUAL = 0, "Manual"
    FORM = 1, "Form"
    IMPORT = 2, "Import"


class ProjectTypeChoices(models.IntegerChoices):
    TECHNICAL = 1, 'Technical'
    BUSINESS = 2, 'Business'
    BALANCED = 3, 'Balanced'


class QuestionTypeChoices(models.IntegerChoices):
    TEXT = 1, "Text Input"      
    CHECKBOX = 2, "Checkbox"


class StudentIntakeFormTypeChoices(models.IntegerChoices):
    TEXT = 1, "Text Input"      
    CHECKBOX = 2, "Checkbox"


class ReviewStatusChoices(models.IntegerChoices):
    PENDING = 1, "Pending"
    IN_PROGRESS = 2, "In Progress"
    COMPLETED = 3, "Completed"


class ReflectionAndInTakeTypeChoices(models.IntegerChoices):
    REFLECTION = 1, "Reflection"      
    INTAKE = 2, "InTake"


class PaymentStatusChoices(models.IntegerChoices):
    PENDING = 0, 'Pending'
    COMPLETED = 1, 'Completed'
    FAILED = 2, 'Failed'

class SubStatus(models.IntegerChoices):
    PREVIEW = 1, 'Free Preview (Blurred)'
    ACTIVE = 2, 'Active Subscriber'
    PAST_DUE = 3, 'Grace Period / Failed'
    CANCELED = 4, 'Canceled'

class EngineProvider(models.IntegerChoices):
    GOOGLE_VISION = 1, 'Google Vision'
    BING_SEARCH = 2, 'Bing Image Search'
    AWS_REKOGNITION = 3, 'AWS Liveness'

class PaymentStatus(models.IntegerChoices):
    SUCCESS = 1, 'Success'
    FAILED = 2, 'Failed'
    REFUNDED = 3, 'Refunded'





