"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-11-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
import uuid

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('avatar', sa.String(500), nullable=True),
        sa.Column('role', sa.Enum('owner', 'admin', 'developer', 'viewer', name='userrole'), default='developer', nullable=False),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('is_superuser', sa.Boolean, default=False),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Teams table
    op.create_table(
        'teams',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False, index=True),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('avatar', sa.String(500), nullable=True),
        sa.Column('owner_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Team Members table
    op.create_table(
        'team_members',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=False),
        sa.Column('role', sa.Enum('owner', 'admin', 'developer', 'viewer', name='userrole'), default='developer', nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('user_id', 'team_id', name='uq_user_team'),
    )
    op.create_index('ix_team_members_user_id', 'team_members', ['user_id'])
    op.create_index('ix_team_members_team_id', 'team_members', ['team_id'])

    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('team_id', UUID(as_uuid=True), sa.ForeignKey('teams.id'), nullable=False, index=True),
        sa.Column('repository_url', sa.String(500), nullable=True),
        sa.Column('branch', sa.String(100), default='main', nullable=False),
        sa.Column('framework', sa.String(100), nullable=True),
        sa.Column('language', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('pending', 'scanning', 'analyzed', 'stabilizing', 'ready', 'error', name='projectstatus'), default='pending', nullable=False),
        sa.Column('demo_survival_score', sa.Integer, nullable=True),
        sa.Column('critical_issues', sa.Integer, default=0),
        sa.Column('feature_reliability', sa.Float, nullable=True),
        sa.Column('demo_readiness', sa.Integer, nullable=True),
        sa.Column('last_scan_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('storage_path', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Scan Sessions table
    op.create_table(
        'scan_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', name='scanstatus'), default='pending', nullable=False),
        sa.Column('progress', sa.Integer, default=0),
        sa.Column('current_step', sa.String(200), default=''),
        sa.Column('total_files', sa.Integer, default=0),
        sa.Column('scanned_files', sa.Integer, default=0),
        sa.Column('languages', JSON, default=list),
        sa.Column('frameworks', JSON, default=list),
        sa.Column('dependencies', JSON, default=list),
        sa.Column('issues', JSON, default=list),
        sa.Column('secrets', JSON, default=list),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Scan Findings table
    op.create_table(
        'scan_findings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('scan_session_id', UUID(as_uuid=True), sa.ForeignKey('scan_sessions.id'), nullable=False, index=True),
        sa.Column('type', sa.Enum('error', 'warning', 'info', name='issuetype'), nullable=False),
        sa.Column('category', sa.Enum('import', 'dependency', 'config', 'security', 'performance', 'style', name='issuecategory'), nullable=False),
        sa.Column('file', sa.String(500), nullable=False),
        sa.Column('line', sa.Integer, nullable=True),
        sa.Column('column', sa.Integer, nullable=True),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('rule', sa.String(200), nullable=True),
        sa.Column('fixable', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )

    # Secret Findings table
    op.create_table(
        'secret_findings',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('scan_session_id', UUID(as_uuid=True), sa.ForeignKey('scan_sessions.id'), nullable=False, index=True),
        sa.Column('type', sa.String(100), nullable=False),
        sa.Column('file', sa.String(500), nullable=False),
        sa.Column('line', sa.Integer, nullable=False),
        sa.Column('severity', sa.Enum('critical', 'high', 'medium', 'low', name='risklevel'), nullable=False),
        sa.Column('matched_content', sa.Text, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )

    # Features table
    op.create_table(
        'features',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('path', sa.String(500), nullable=False),
        sa.Column('type', sa.Enum('api', 'ui', 'service', 'database', 'auth', 'integration', name='featuretype'), nullable=False),
        sa.Column('status', sa.Enum('unknown', 'stable', 'unstable', 'critical', 'mocked', name='featurestatus'), default='unknown', nullable=False),
        sa.Column('reliability_score', sa.Integer, default=0),
        sa.Column('dependencies', ARRAY(sa.String), default=list),
        sa.Column('test_coverage', sa.Float, nullable=True),
        sa.Column('last_tested_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('demo_path', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Feature Dependencies table
    op.create_table(
        'feature_dependencies',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('source_feature_id', UUID(as_uuid=True), sa.ForeignKey('features.id'), nullable=False),
        sa.Column('target_feature_id', UUID(as_uuid=True), sa.ForeignKey('features.id'), nullable=False),
        sa.Column('type', sa.String(50), default='requires'),
        sa.Column('strength', sa.String(50), default='strong'),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.UniqueConstraint('source_feature_id', 'target_feature_id', name='uq_feature_dependency'),
    )

    # Risk Assessments table
    op.create_table(
        'risk_assessments',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('overall_score', sa.Integer, default=0),
        sa.Column('risk_level', sa.Enum('critical', 'high', 'medium', 'low', name='risklevel'), default='low', nullable=False),
        sa.Column('risk_distribution', JSON, default=dict),
        sa.Column('feature_scores', JSON, default=list),
        sa.Column('failure_predictions', JSON, default=list),
        sa.Column('happy_paths', JSON, default=list),
        sa.Column('dependency_risks', JSON, default=list),
        sa.Column('ai_recommendations', JSON, default=list),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Stabilization Tasks table
    op.create_table(
        'stabilization_tasks',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('type', sa.Enum('patch', 'mock', 'fallback', 'config', 'test', 'refactor', name='tasktype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'approved', 'rejected', 'applied', 'rolled_back', 'testing', name='taskstatus'), default='pending', nullable=False),
        sa.Column('priority', sa.Enum('critical', 'high', 'medium', 'low', name='risklevel'), default='medium', nullable=False),
        sa.Column('files', JSON, default=list),
        sa.Column('ai_recommendation_id', sa.String(100), nullable=True),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('approved_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rolled_back_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Patches table
    op.create_table(
        'patches',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('task_id', UUID(as_uuid=True), sa.ForeignKey('stabilization_tasks.id'), nullable=False, index=True),
        sa.Column('file_path', sa.String(500), nullable=False),
        sa.Column('original_content', sa.Text, nullable=False),
        sa.Column('modified_content', sa.Text, nullable=False),
        sa.Column('diff', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), default='pending'),
        sa.Column('approved_by', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('applied_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('rolled_back_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )

    # Test Executions table
    op.create_table(
        'test_executions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('scan_session_id', UUID(as_uuid=True), sa.ForeignKey('scan_sessions.id'), nullable=True),
        sa.Column('stabilization_task_id', UUID(as_uuid=True), sa.ForeignKey('stabilization_tasks.id'), nullable=True),
        sa.Column('type', sa.Enum('smoke', 'happy_path', 'api', 'ui', 'regression', 'environment', 'demo_readiness', name='testtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'passed', 'failed', 'skipped', 'unverified', name='teststatus'), default='pending', nullable=False),
        sa.Column('tests', JSON, default=list),
        sa.Column('passed_count', sa.Integer, default=0),
        sa.Column('failed_count', sa.Integer, default=0),
        sa.Column('skipped_count', sa.Integer, default=0),
        sa.Column('total_duration', sa.Integer, default=0),
        sa.Column('environment', JSON, default=dict),
        sa.Column('error', sa.Text, nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )

    # Demo Configurations table
    op.create_table(
        'demo_configurations',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('name', sa.String(200), default='Default Demo Config'),
        sa.Column('enabled', sa.Boolean, default=False),
        sa.Column('mock_data', JSON, default=list),
        sa.Column('api_fallbacks', JSON, default=list),
        sa.Column('feature_flags', JSON, default=list),
        sa.Column('environment_variables', JSON, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Demo Scripts table
    op.create_table(
        'demo_scripts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('title', sa.String(300), nullable=False),
        sa.Column('duration_minutes', sa.Integer, default=10),
        sa.Column('audience', sa.String(50), default='judges'),
        sa.Column('sections', JSON, default=list),
        sa.Column('verified_features_only', sa.Boolean, default=True),
        sa.Column('generated_at', sa.DateTime(timezone=True), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Activity Logs table
    op.create_table(
        'activity_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('action', sa.String(200), nullable=False),
        sa.Column('entity_type', sa.String(100), nullable=False),
        sa.Column('entity_id', UUID(as_uuid=True), nullable=False),
        sa.Column('metadata', JSON, default=dict),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_index('ix_activity_logs_created_at', 'activity_logs', ['created_at'])

    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('type', sa.Enum('info', 'warning', 'error', 'success', name='notificationtype'), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('read', sa.Boolean, default=False),
        sa.Column('action_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_index('ix_notifications_read', 'notifications', ['read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])

    # Git Commits table
    op.create_table(
        'git_commits',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('project_id', UUID(as_uuid=True), sa.ForeignKey('projects.id'), nullable=False, index=True),
        sa.Column('sha', sa.String(40), nullable=False),
        sa.Column('message', sa.Text, nullable=False),
        sa.Column('author', sa.String(200), nullable=False),
        sa.Column('author_email', sa.String(200), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('files_changed', JSON, default=list),
        sa.Column('risk_level', sa.Enum('critical', 'high', 'medium', 'low', name='risklevel'), default='low', nullable=False),
        sa.Column('risk_reason', sa.Text, nullable=True),
        sa.Column('affects_demo_path', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), default=sa.func.now()),
    )
    op.create_index('ix_git_commits_sha', 'git_commits', ['sha'])


def downgrade() -> None:
    op.drop_table('git_commits')
    op.drop_table('notifications')
    op.drop_table('activity_logs')
    op.drop_table('demo_scripts')
    op.drop_table('demo_configurations')
    op.drop_table('test_executions')
    op.drop_table('patches')
    op.drop_table('stabilization_tasks')
    op.drop_table('risk_assessments')
    op.drop_table('feature_dependencies')
    op.drop_table('features')
    op.drop_table('secret_findings')
    op.drop_table('scan_findings')
    op.drop_table('scan_sessions')
    op.drop_table('projects')
    op.drop_table('team_members')
    op.drop_table('teams')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS projectstatus")
    op.execute("DROP TYPE IF EXISTS scanstatus")
    op.execute("DROP TYPE IF EXISTS issuetype")
    op.execute("DROP TYPE IF EXISTS issuecategory")
    op.execute("DROP TYPE IF EXISTS risklevel")
    op.execute("DROP TYPE IF EXISTS featuretype")
    op.execute("DROP TYPE IF EXISTS featurestatus")
    op.execute("DROP TYPE IF EXISTS tasktype")
    op.execute("DROP TYPE IF EXISTS taskstatus")
    op.execute("DROP TYPE IF EXISTS testtype")
    op.execute("DROP TYPE IF EXISTS teststatus")
    op.execute("DROP TYPE IF EXISTS notificationtype")