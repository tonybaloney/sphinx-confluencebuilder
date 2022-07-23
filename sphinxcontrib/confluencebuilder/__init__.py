# -*- coding: utf-8 -*-
"""
:copyright: Copyright 2016-2022 Sphinx Confluence Builder Contributors (AUTHORS)
:license: BSD-2-Clause (LICENSE)
"""

from os import path
from sphinx.util import docutils
from sphinxcontrib.confluencebuilder.builder import ConfluenceBuilder
from sphinxcontrib.confluencebuilder.config import handle_config_inited
from sphinxcontrib.confluencebuilder.config.manager import ConfigManager
from sphinxcontrib.confluencebuilder.directives import ConfluenceExpandDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceLatexDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceMetadataDirective
from sphinxcontrib.confluencebuilder.directives import ConfluenceNewline
from sphinxcontrib.confluencebuilder.directives import ConfluenceToc
from sphinxcontrib.confluencebuilder.directives import JiraDirective
from sphinxcontrib.confluencebuilder.directives import JiraIssueDirective
from sphinxcontrib.confluencebuilder.locale import MESSAGE_CATALOG_NAME
from sphinxcontrib.confluencebuilder.logger import ConfluenceLogger
from sphinxcontrib.confluencebuilder.nodes import confluence_metadata
from sphinxcontrib.confluencebuilder.nodes import jira
from sphinxcontrib.confluencebuilder.nodes import jira_issue
from sphinxcontrib.confluencebuilder.reportbuilder import ConfluenceReportBuilder
from sphinxcontrib.confluencebuilder.roles import ConfluenceEmoticonRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceLatexRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceMentionRole
from sphinxcontrib.confluencebuilder.roles import ConfluenceStatusRole
from sphinxcontrib.confluencebuilder.roles import JiraRole
from sphinxcontrib.confluencebuilder.singlebuilder import SingleConfluenceBuilder

# load autosummary extension if available to add additional nodes
try:
    from sphinx.ext import autosummary
except ImportError:
    autosummary = None

# load imgmath extension if available to handle math configuration options
try:
    from sphinx.ext import imgmath
except ImportError:
    imgmath = None

__version__ = '1.9.0.dev0'


def setup(app):
    ConfluenceLogger.initialize()
    cm = app.config_manager_ = ConfigManager(app)

    app.require_sphinx('1.8')
    app.add_builder(ConfluenceBuilder)
    app.add_builder(ConfluenceReportBuilder)
    app.add_builder(SingleConfluenceBuilder)

    # register this extension's locale
    package_dir = path.abspath(path.dirname(__file__))
    locale_dir = path.join(package_dir, 'locale')
    app.add_message_catalog(MESSAGE_CATALOG_NAME, locale_dir)

    # ##########################################################################

    # (configuration - essential)
    # Enablement of publishing.
    cm.add_conf_bool('confluence_publish')
    # PAT to authenticate to Confluence API with.
    cm.add_conf('confluence_publish_token')
    # API key/password to login to Confluence API with.
    cm.add_conf('confluence_server_pass')
    # URL of the Confluence instance to publish to.
    cm.add_conf('confluence_server_url')
    # Username to login to Confluence API with.
    cm.add_conf('confluence_server_user')
    # Confluence Space to publish to.
    cm.add_conf('confluence_space_key')

    # (configuration - generic)
    # Add page and section numbers if doctree has :numbered: option
    cm.add_conf_bool('confluence_add_secnumbers', 'env')
    # Default alignment for tables, figures, etc.
    cm.add_conf('confluence_default_alignment', 'env')
    # Enablement of a generated domain index documents
    cm.add_conf('confluence_domain_indices')
    # File to get page header information from.
    cm.add_conf('confluence_header_file', 'env')
    # Dictionary to pass to header when rendering template
    cm.add_conf('confluence_header_data', 'env')
    # File to get page footer information from.
    cm.add_conf('confluence_footer_file', 'env')
    # Dictionary to pass to footer when rendering template.
    cm.add_conf('confluence_footer_data', 'env')
    # Enablement of a generated search documents
    cm.add_conf_bool('confluence_include_search')
    # Enablement of the maximum document depth (before inlining).
    cm.add_conf_int('confluence_max_doc_depth', 'env')
    # Enablement of a "page generated" notice.
    cm.add_conf_bool('confluence_page_generation_notice', 'env')
    # Enablement of publishing pages into a hierarchy from a root toctree.
    cm.add_conf_bool('confluence_page_hierarchy')
    # Show previous/next buttons (bottom, top, both, None).
    cm.add_conf('confluence_prev_next_buttons_location', 'env')
    # Suffix to put after section numbers, before section name
    cm.add_conf('confluence_secnumber_suffix', 'env')
    # Enablement of a "Edit/Show Source" reference on each document
    cm.add_conf('confluence_sourcelink', 'env')
    # Enablement of a generated index document
    cm.add_conf_bool('confluence_use_index')
    # Enablement for toctrees for singleconfluence documents.
    cm.add_conf_bool('singleconfluence_toctree', 'singleconfluence')

    # (configuration - publishing)
    # Request for publish password to come from interactive session.
    cm.add_conf_bool('confluence_ask_password')
    # Request for publish username to come from interactive session.
    cm.add_conf_bool('confluence_ask_user')
    # Explicitly prevent auto-generation of titles for titleless documents.
    cm.add_conf_bool('confluence_disable_autogen_title')
    # Explicitly prevent page notifications on update.
    cm.add_conf_bool('confluence_disable_notifications')
    # Define a series of labels to apply to all published pages.
    cm.add_conf('confluence_global_labels')
    # Enablement of configuring root as space's homepage.
    cm.add_conf_bool('confluence_root_homepage')
    # Parent page's name or identifier to publish documents under.
    cm.add_conf('confluence_parent_page')
    # Perform a dry run of publishing to inspect what publishing will do.
    cm.add_conf_bool('confluence_publish_dryrun')
    # Publish only new content (no page updates, etc.).
    cm.add_conf_bool('confluence_publish_onlynew')
    # Postfix to apply to title of published pages.
    cm.add_conf('confluence_publish_postfix', 'env')
    # Prefix to apply to published pages.
    cm.add_conf('confluence_publish_prefix', 'env')
    # Root page's identifier to publish documents into.
    cm.add_conf_int('confluence_publish_root')
    # Enablement of purging legacy child pages from a parent page.
    cm.add_conf_bool('confluence_purge')
    # Enablement of purging legacy child pages from a root page.
    cm.add_conf_bool('confluence_purge_from_root')
    # docname-2-title dictionary for title overrides.
    cm.add_conf('confluence_title_overrides', 'env')
    # Timeout for network-related calls (publishing).
    cm.add_conf_int('confluence_timeout')
    # Whether or not new content should be watched.
    cm.add_conf_bool('confluence_watch')

    # (configuration - advanced publishing)
    # Register additional mime types to be selected for image candidates.
    cm.add_conf('confluence_additional_mime_types', 'env')
    # Whether or not labels will be appended instead of overwriting them.
    cm.add_conf_bool('confluence_append_labels')
    # Forcing all assets to be standalone.
    cm.add_conf_bool('confluence_asset_force_standalone', 'env')
    # Tri-state asset handling (auto, force push or disable).
    cm.add_conf_bool('confluence_asset_override')
    # File/path to Certificate Authority
    cm.add_conf('confluence_ca_cert')
    # Path to client certificate to use for publishing
    cm.add_conf('confluence_client_cert')
    # Password for client certificate to use for publishing
    cm.add_conf('confluence_client_cert_pass')
    # Disable SSL validation with Confluence server.
    cm.add_conf_bool('confluence_disable_ssl_validation')
    # Ignore adding a titlefix on the index document.
    cm.add_conf_bool('confluence_ignore_titlefix_on_index', 'env')
    # Parent page's identifier to publish documents under.
    cm.add_conf_int('confluence_parent_page_id_check')
    # Proxy server needed to communicate with Confluence server.
    cm.add_conf('confluence_proxy')
    # Subset of documents which are allowed to be published.
    cm.add_conf('confluence_publish_allowlist')
    # Enable debugging for publish requests.
    cm.add_conf_bool('confluence_publish_debug')
    # Duration (in seconds) to delay each API request.
    cm.add_conf('confluence_publish_delay')
    # Subset of documents which are denied to be published.
    cm.add_conf('confluence_publish_denylist')
    # Disable adding `rest/api` to REST requests.
    cm.add_conf_bool('confluence_publish_disable_api_prefix')
    # Header(s) to use for Confluence REST interaction.
    cm.add_conf('confluence_publish_headers')
    # Whether to publish a generated intersphinx database to the root document
    cm.add_conf_bool('confluence_publish_intersphinx')
    # Manipulate a requests instance.
    cm.add_conf('confluence_request_session_override')
    # Authentication passthrough for Confluence REST interaction.
    cm.add_conf('confluence_server_auth')
    # Cookie(s) to use for Confluence REST interaction.
    cm.add_conf('confluence_server_cookies')
    # Comment added to confluence version history.
    cm.add_conf('confluence_version_comment')

    # (configuration - advanced processing)
    # Filename suffix for generated files.
    cm.add_conf('confluence_file_suffix', 'env')
    # Translation of docname to a filename.
    cm.add_conf('confluence_file_transform', 'env')
    # Configuration for named JIRA Servers
    cm.add_conf('confluence_jira_servers', 'env')
    # Translation of a raw language to code block macro language.
    cm.add_conf('confluence_lang_transform', 'env')
    # Macro configuration for Confluence-managed LaTeX content.
    cm.add_conf('confluence_latex_macro', 'env')
    # Link suffix for generated files.
    cm.add_conf('confluence_link_suffix', 'env')
    # Translation of docname to a (partial) URI.
    cm.add_conf('confluence_link_transform', 'env')
    # Mappings for documentation mentions to Confluence keys.
    cm.add_conf('confluence_mentions', 'env')
    # Inject navigational hints into the documentation.
    cm.add_conf('confluence_navdocs_transform')
    # Remove a detected title from generated documents.
    cm.add_conf_bool('confluence_remove_title', 'env')

    # (configuration - undocumented)
    # Enablement for aggressive descendents search (for purge).
    cm.add_conf_bool('confluence_adv_aggressive_search')
    # List of node types to ignore if no translator support exists.
    cm.add_conf('confluence_adv_ignore_nodes')
    # Unknown node handler dictionary for advanced integrations.
    cm.add_conf('confluence_adv_node_handler')
    # Enablement of permitting raw html blocks to be used in storage format.
    cm.add_conf_bool('confluence_adv_permit_raw_html', 'env')
    # List of optional features/macros/etc. restricted for use.
    cm.add_conf('confluence_adv_restricted', 'env')
    # Enablement of tracing processed data.
    cm.add_conf_bool('confluence_adv_trace_data')
    # Do not cap sections to a maximum of six (6) levels.
    cm.add_conf_bool('confluence_adv_writer_no_section_cap', 'env')

    # (configuration - deprecated)
    # replaced by confluence_root_homepage
    cm.add_conf('confluence_master_homepage')
    # replaced by confluence_publish_allowlist
    cm.add_conf('confluence_publish_subset')
    # replaced by confluence_purge_from_root
    cm.add_conf_bool('confluence_purge_from_master')
    # replaced by confluence_space_key
    cm.add_conf('confluence_space_name')

    # ##########################################################################

    # hook onto configuration initialization to finalize its state before
    # passing it to the builder (e.g. handling deprecated options)
    app.connect('config-inited', handle_config_inited)

    # hook on a builder initialization event, to perform additional
    # configuration required when a user is using a confluence builder
    app.connect('builder-inited', confluence_builder_inited)

    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }


def confluence_builder_inited(app):
    """
    invoked when the configured sphinx builder is initialized

    Handling a `builder-inited` event generated from Sphinx.
    """

    # ignore non-confluence builder types
    if not isinstance(app.builder, ConfluenceBuilder):
        return

    # register nodes required by confluence-specific directives
    if not docutils.is_node_registered(confluence_metadata):
        app.add_node(confluence_metadata)
    if not docutils.is_node_registered(jira):
        app.add_node(jira)
    if not docutils.is_node_registered(jira_issue):
        app.add_node(jira_issue)

    # register directives
    app.add_directive('confluence_expand', ConfluenceExpandDirective)
    app.add_directive('confluence_latex', ConfluenceLatexDirective)
    app.add_directive('confluence_metadata', ConfluenceMetadataDirective)
    app.add_directive('confluence_newline', ConfluenceNewline)
    app.add_directive('confluence_toc', ConfluenceToc)
    app.add_directive('jira', JiraDirective)
    app.add_directive('jira_issue', JiraIssueDirective)

    # register roles
    app.add_role('confluence_emoticon', ConfluenceEmoticonRole)
    app.add_role('confluence_latex', ConfluenceLatexRole)
    app.add_role('confluence_mention', ConfluenceMentionRole)
    app.add_role('confluence_status', ConfluenceStatusRole)
    app.add_role('jira', JiraRole)

    # inject compatible autosummary nodes if the extension is available/loaded
    if autosummary:
        for ext in app.extensions.values():
            if ext.name == 'sphinx.ext.autosummary':
                app.registry.add_translation_handlers(
                    autosummary.autosummary_table,
                    confluence=(
                        autosummary.autosummary_table_visit_html,
                        autosummary.autosummary_noop,
                    ),
                    singleconfluence=(
                        autosummary.autosummary_table_visit_html,
                        autosummary.autosummary_noop,
                    ),
                )
                app.registry.add_translation_handlers(
                    autosummary.autosummary_toc,
                    confluence=(
                        autosummary.autosummary_toc_visit_html,
                        autosummary.autosummary_noop,
                    ),
                    singleconfluence=(
                        autosummary.autosummary_toc_visit_html,
                        autosummary.autosummary_noop,
                    ),
                )
                break

    # lazy bind sphinx.ext.imgmath to provide configuration options
    #
    # If 'sphinx.ext.imgmath' is not already explicitly loaded, bind it into the
    # setup process to a configurer can use the same configuration options
    # outlined in the sphinx.ext.imgmath in this extension. This applies for
    # Sphinx 1.8 and higher which math support is embedded; for older versions,
    # users will need to explicitly load 'sphinx.ext.mathbase'.
    if imgmath is not None:
        if 'sphinx.ext.imgmath' not in app.config.extensions:
            imgmath.setup(app)

    # remove math-node-migration post-transform as this extension manages both
    # future and legacy math implementations (removing this transform removes
    # a warning notification to the user)
    for transform in app.registry.get_post_transforms():
        if transform.__name__ == 'MathNodeMigrator':
            app.registry.get_post_transforms().remove(transform)
            break
