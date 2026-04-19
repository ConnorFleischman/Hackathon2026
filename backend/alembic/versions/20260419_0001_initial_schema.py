"""initial backend schema

Revision ID: 20260419_0001
Revises:
Create Date: 2026-04-19 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260419_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = sa.Enum("user", "moderator", "admin", "super_admin", "org_account", name="user_role")
user_status_enum = sa.Enum("pending_verification", "active", "suspended", "banned", name="user_status")
post_type_enum = sa.Enum("standard", "announcement", "event", "safety_alert", name="post_type")
visibility_status_enum = sa.Enum(
    "pending_moderation",
    "visible",
    "hidden",
    "archived",
    "removed",
    "expired",
    name="visibility_status",
)
moderation_status_enum = sa.Enum("pending", "approved", "flagged", "auto_hidden", "rejected", name="moderation_status")
reaction_type_enum = sa.Enum("like", "dislike", name="reaction_type")
report_status_enum = sa.Enum("open", "reviewing", "resolved", "dismissed", name="report_status")
location_source_enum = sa.Enum("gps", "manual", "admin", name="location_source")
flag_source_enum = sa.Enum("ai", "user_report", "admin", name="flag_source")
flag_type_enum = sa.Enum("harassment", "threat", "hate_speech", "spam", "self_harm", "other", name="flag_type")
flag_decision_enum = sa.Enum("pending_review", "allowed", "hidden", "removed", name="flag_decision")
report_target_type_enum = sa.Enum("post", "comment", "user", name="report_target_type")


def upgrade() -> None:
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    user_status_enum.create(bind, checkfirst=True)
    post_type_enum.create(bind, checkfirst=True)
    visibility_status_enum.create(bind, checkfirst=True)
    moderation_status_enum.create(bind, checkfirst=True)
    reaction_type_enum.create(bind, checkfirst=True)
    report_status_enum.create(bind, checkfirst=True)
    location_source_enum.create(bind, checkfirst=True)
    flag_source_enum.create(bind, checkfirst=True)
    flag_type_enum.create(bind, checkfirst=True)
    flag_decision_enum.create(bind, checkfirst=True)
    report_target_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "campuses",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("slug", sa.String(length=150), nullable=False),
        sa.Column("city", sa.String(length=120), nullable=True),
        sa.Column("state", sa.String(length=120), nullable=True),
        sa.Column("country", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_campuses")),
        sa.UniqueConstraint("name", name=op.f("uq_campuses_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_campuses_slug")),
    )
    op.create_index(op.f("ix_campuses_slug"), "campuses", ["slug"], unique=False)

    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_categories")),
        sa.UniqueConstraint("name", name=op.f("uq_categories_name")),
        sa.UniqueConstraint("slug", name=op.f("uq_categories_slug")),
    )
    op.create_index(op.f("ix_categories_slug"), "categories", ["slug"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("campus_id", sa.Uuid(), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("display_name", sa.String(length=120), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", user_role_enum, server_default=sa.text("'user'"), nullable=False),
        sa.Column("status", user_status_enum, server_default=sa.text("'pending_verification'"), nullable=False),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["campus_id"], ["campuses.id"], name=op.f("fk_users_campus_id_campuses"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_index(op.f("ix_users_campus_id"), "users", ["campus_id"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=False)
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=False)

    op.create_table(
        "admin_actions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("admin_user_id", sa.Uuid(), nullable=True),
        sa.Column("target_user_id", sa.Uuid(), nullable=True),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["admin_user_id"],
            ["users.id"],
            name=op.f("fk_admin_actions_admin_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["target_user_id"],
            ["users.id"],
            name=op.f("fk_admin_actions_target_user_id_users"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_admin_actions")),
    )
    op.create_index(op.f("ix_admin_actions_action_type"), "admin_actions", ["action_type"], unique=False)
    op.create_index(op.f("ix_admin_actions_admin_user_id"), "admin_actions", ["admin_user_id"], unique=False)
    op.create_index(op.f("ix_admin_actions_target_user_id"), "admin_actions", ["target_user_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_user_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(length=150), nullable=False),
        sa.Column("entity_type", sa.String(length=120), nullable=False),
        sa.Column("entity_id", sa.Uuid(), nullable=True),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], name=op.f("fk_audit_logs_actor_user_id_users"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_audit_logs")),
    )
    op.create_index(op.f("ix_audit_logs_action"), "audit_logs", ["action"], unique=False)
    op.create_index(op.f("ix_audit_logs_actor_user_id"), "audit_logs", ["actor_user_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)

    op.create_table(
        "bans",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("issued_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("lifted_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("lifted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["issued_by_user_id"], ["users.id"], name=op.f("fk_bans_issued_by_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lifted_by_user_id"], ["users.id"], name=op.f("fk_bans_lifted_by_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_bans_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_bans")),
    )
    op.create_index(op.f("ix_bans_issued_by_user_id"), "bans", ["issued_by_user_id"], unique=False)
    op.create_index(op.f("ix_bans_lifted_by_user_id"), "bans", ["lifted_by_user_id"], unique=False)
    op.create_index(op.f("ix_bans_user_id"), "bans", ["user_id"], unique=False)

    op.create_table(
        "posts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("campus_id", sa.Uuid(), nullable=True),
        sa.Column("category_id", sa.Uuid(), nullable=True),
        sa.Column("type", post_type_enum, server_default=sa.text("'standard'"), nullable=False),
        sa.Column("visibility_status", visibility_status_enum, server_default=sa.text("'pending_moderation'"), nullable=False),
        sa.Column("moderation_status", moderation_status_enum, server_default=sa.text("'pending'"), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("event_name", sa.String(length=200), nullable=True),
        sa.Column("event_location", sa.String(length=255), nullable=True),
        sa.Column("event_start_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("event_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "event_end_at IS NULL OR event_start_at IS NULL OR event_end_at >= event_start_at",
            name=op.f("ck_posts_post_event_window_valid"),
        ),
        sa.ForeignKeyConstraint(["campus_id"], ["campuses.id"], name=op.f("fk_posts_campus_id_campuses"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], name=op.f("fk_posts_category_id_categories"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_posts_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_posts")),
    )
    op.create_index(op.f("ix_posts_campus_id"), "posts", ["campus_id"], unique=False)
    op.create_index(op.f("ix_posts_category_id"), "posts", ["category_id"], unique=False)
    op.create_index(op.f("ix_posts_expires_at"), "posts", ["expires_at"], unique=False)
    op.create_index(op.f("ix_posts_moderation_status"), "posts", ["moderation_status"], unique=False)
    op.create_index(op.f("ix_posts_type"), "posts", ["type"], unique=False)
    op.create_index(op.f("ix_posts_user_id"), "posts", ["user_id"], unique=False)
    op.create_index(op.f("ix_posts_visibility_status"), "posts", ["visibility_status"], unique=False)

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_sessions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_sessions")),
        sa.UniqueConstraint("refresh_token_hash", name=op.f("uq_sessions_refresh_token_hash")),
    )
    op.create_index(op.f("ix_sessions_expires_at"), "sessions", ["expires_at"], unique=False)
    op.create_index(op.f("ix_sessions_user_id"), "sessions", ["user_id"], unique=False)

    op.create_table(
        "user_locations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("campus_id", sa.Uuid(), nullable=True),
        sa.Column("latitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("longitude", sa.Numeric(precision=9, scale=6), nullable=True),
        sa.Column("source", location_source_enum, server_default=sa.text("'gps'"), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["campus_id"], ["campuses.id"], name=op.f("fk_user_locations_campus_id_campuses"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_locations_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_locations")),
    )
    op.create_index(op.f("ix_user_locations_campus_id"), "user_locations", ["campus_id"], unique=False)
    op.create_index(op.f("ix_user_locations_recorded_at"), "user_locations", ["recorded_at"], unique=False)
    op.create_index(op.f("ix_user_locations_user_id"), "user_locations", ["user_id"], unique=False)

    op.create_table(
        "comments",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("parent_comment_id", sa.Uuid(), nullable=True),
        sa.Column("visibility_status", visibility_status_enum, server_default=sa.text("'visible'"), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["parent_comment_id"], ["comments.id"], name=op.f("fk_comments_parent_comment_id_comments"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name=op.f("fk_comments_post_id_posts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_comments_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comments")),
    )
    op.create_index(op.f("ix_comments_parent_comment_id"), "comments", ["parent_comment_id"], unique=False)
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(op.f("ix_comments_user_id"), "comments", ["user_id"], unique=False)

    op.create_table(
        "reactions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("reaction_type", reaction_type_enum, server_default=sa.text("'like'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name=op.f("fk_reactions_post_id_posts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_reactions_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reactions")),
        sa.UniqueConstraint("post_id", "user_id", name="uq_reactions_post_user"),
    )
    op.create_index(op.f("ix_reactions_post_id"), "reactions", ["post_id"], unique=False)
    op.create_index(op.f("ix_reactions_user_id"), "reactions", ["user_id"], unique=False)

    op.create_table(
        "reports",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("reporter_user_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", report_target_type_enum, nullable=False),
        sa.Column("target_post_id", sa.Uuid(), nullable=True),
        sa.Column("target_comment_id", sa.Uuid(), nullable=True),
        sa.Column("target_user_id", sa.Uuid(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", report_status_enum, server_default=sa.text("'open'"), nullable=False),
        sa.Column("resolver_notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(target_post_id IS NOT NULL)::int + (target_comment_id IS NOT NULL)::int + (target_user_id IS NOT NULL)::int = 1",
            name=op.f("ck_reports_report_single_target"),
        ),
        sa.ForeignKeyConstraint(["reporter_user_id"], ["users.id"], name=op.f("fk_reports_reporter_user_id_users"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_comment_id"], ["comments.id"], name=op.f("fk_reports_target_comment_id_comments"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_post_id"], ["posts.id"], name=op.f("fk_reports_target_post_id_posts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["target_user_id"], ["users.id"], name=op.f("fk_reports_target_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_reports")),
    )
    op.create_index(op.f("ix_reports_reporter_user_id"), "reports", ["reporter_user_id"], unique=False)
    op.create_index(op.f("ix_reports_status"), "reports", ["status"], unique=False)
    op.create_index(op.f("ix_reports_target_comment_id"), "reports", ["target_comment_id"], unique=False)
    op.create_index(op.f("ix_reports_target_post_id"), "reports", ["target_post_id"], unique=False)
    op.create_index(op.f("ix_reports_target_type"), "reports", ["target_type"], unique=False)
    op.create_index(op.f("ix_reports_target_user_id"), "reports", ["target_user_id"], unique=False)

    op.create_table(
        "post_flags",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("post_id", sa.Uuid(), nullable=True),
        sa.Column("comment_id", sa.Uuid(), nullable=True),
        sa.Column("source", flag_source_enum, nullable=False),
        sa.Column("flag_type", flag_type_enum, nullable=False),
        sa.Column("decision", flag_decision_enum, server_default=sa.text("'pending_review'"), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("reviewed_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint(
            "(post_id IS NOT NULL AND comment_id IS NULL) OR (post_id IS NULL AND comment_id IS NOT NULL)",
            name=op.f("ck_post_flags_post_flag_single_target"),
        ),
        sa.ForeignKeyConstraint(["comment_id"], ["comments.id"], name=op.f("fk_post_flags_comment_id_comments"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by_user_id"], ["users.id"], name=op.f("fk_post_flags_created_by_user_id_users"), ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["post_id"], ["posts.id"], name=op.f("fk_post_flags_post_id_posts"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_user_id"], ["users.id"], name=op.f("fk_post_flags_reviewed_by_user_id_users"), ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_post_flags")),
    )
    op.create_index(op.f("ix_post_flags_comment_id"), "post_flags", ["comment_id"], unique=False)
    op.create_index(op.f("ix_post_flags_created_by_user_id"), "post_flags", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_post_flags_decision"), "post_flags", ["decision"], unique=False)
    op.create_index(op.f("ix_post_flags_post_id"), "post_flags", ["post_id"], unique=False)
    op.create_index(op.f("ix_post_flags_reviewed_by_user_id"), "post_flags", ["reviewed_by_user_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_post_flags_reviewed_by_user_id"), table_name="post_flags")
    op.drop_index(op.f("ix_post_flags_post_id"), table_name="post_flags")
    op.drop_index(op.f("ix_post_flags_decision"), table_name="post_flags")
    op.drop_index(op.f("ix_post_flags_created_by_user_id"), table_name="post_flags")
    op.drop_index(op.f("ix_post_flags_comment_id"), table_name="post_flags")
    op.drop_table("post_flags")

    op.drop_index(op.f("ix_reports_target_user_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_target_type"), table_name="reports")
    op.drop_index(op.f("ix_reports_target_post_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_target_comment_id"), table_name="reports")
    op.drop_index(op.f("ix_reports_status"), table_name="reports")
    op.drop_index(op.f("ix_reports_reporter_user_id"), table_name="reports")
    op.drop_table("reports")

    op.drop_index(op.f("ix_reactions_user_id"), table_name="reactions")
    op.drop_index(op.f("ix_reactions_post_id"), table_name="reactions")
    op.drop_table("reactions")

    op.drop_index(op.f("ix_comments_user_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_parent_comment_id"), table_name="comments")
    op.drop_table("comments")

    op.drop_index(op.f("ix_user_locations_user_id"), table_name="user_locations")
    op.drop_index(op.f("ix_user_locations_recorded_at"), table_name="user_locations")
    op.drop_index(op.f("ix_user_locations_campus_id"), table_name="user_locations")
    op.drop_table("user_locations")

    op.drop_index(op.f("ix_sessions_user_id"), table_name="sessions")
    op.drop_index(op.f("ix_sessions_expires_at"), table_name="sessions")
    op.drop_table("sessions")

    op.drop_index(op.f("ix_posts_visibility_status"), table_name="posts")
    op.drop_index(op.f("ix_posts_user_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_type"), table_name="posts")
    op.drop_index(op.f("ix_posts_moderation_status"), table_name="posts")
    op.drop_index(op.f("ix_posts_expires_at"), table_name="posts")
    op.drop_index(op.f("ix_posts_category_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_campus_id"), table_name="posts")
    op.drop_table("posts")

    op.drop_index(op.f("ix_bans_user_id"), table_name="bans")
    op.drop_index(op.f("ix_bans_lifted_by_user_id"), table_name="bans")
    op.drop_index(op.f("ix_bans_issued_by_user_id"), table_name="bans")
    op.drop_table("bans")

    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_user_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_action"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_admin_actions_target_user_id"), table_name="admin_actions")
    op.drop_index(op.f("ix_admin_actions_admin_user_id"), table_name="admin_actions")
    op.drop_index(op.f("ix_admin_actions_action_type"), table_name="admin_actions")
    op.drop_table("admin_actions")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_campus_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_categories_slug"), table_name="categories")
    op.drop_table("categories")

    op.drop_index(op.f("ix_campuses_slug"), table_name="campuses")
    op.drop_table("campuses")

    report_target_type_enum.drop(op.get_bind(), checkfirst=True)
    flag_decision_enum.drop(op.get_bind(), checkfirst=True)
    flag_type_enum.drop(op.get_bind(), checkfirst=True)
    flag_source_enum.drop(op.get_bind(), checkfirst=True)
    location_source_enum.drop(op.get_bind(), checkfirst=True)
    report_status_enum.drop(op.get_bind(), checkfirst=True)
    reaction_type_enum.drop(op.get_bind(), checkfirst=True)
    moderation_status_enum.drop(op.get_bind(), checkfirst=True)
    visibility_status_enum.drop(op.get_bind(), checkfirst=True)
    post_type_enum.drop(op.get_bind(), checkfirst=True)
    user_status_enum.drop(op.get_bind(), checkfirst=True)
    user_role_enum.drop(op.get_bind(), checkfirst=True)
