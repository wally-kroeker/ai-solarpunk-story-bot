from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import logging

# Import validation after world data module is loaded to avoid circular imports
from src.error_handler import (
    handle_errors, 
    ErrorCategory, 
    ErrorSeverity,
    with_error_reporting,
    logger as error_logger
)

from src.ai_solarpunk import world_parser

logger = logging.getLogger(__name__)

@dataclass
class Technology:
    """Represents a specific technology within the world."""
    name: str
    description: str
    era: int
    impact: str

@dataclass
class Faction:
    """Represents a faction or group in the world."""
    name: str
    description: str
    values: List[str] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)

@dataclass
class CharacterArchetype:
    """Represents a character archetype."""
    name: str
    description: str
    typical_traits: List[str] = field(default_factory=list)
    common_factions: List[str] = field(default_factory=list)

@dataclass
class PlotSeed:
    """Represents a plot seed or story prompt."""
    premise: str
    themes: List[str] = field(default_factory=list)
    potential_conflicts: List[str] = field(default_factory=list)

@dataclass
class Era:
    """Represents a distinct era in the world's timeline."""
    id: int
    name: str
    description: str
    technologies: List[Technology] = field(default_factory=list)
    factions: List[Faction] = field(default_factory=list)
    archetypes: List[CharacterArchetype] = field(default_factory=list)
    plot_seeds: List[PlotSeed] = field(default_factory=list)
    
    @property
    def themes(self) -> List[str]:
        """Extract unique themes from all plot seeds in this era."""
        all_themes = []
        for plot_seed in self.plot_seeds:
            all_themes.extend(plot_seed.themes)
        unique_themes = []
        for theme in all_themes:
            if theme not in unique_themes:
                unique_themes.append(theme)
        return unique_themes

class WorldDataLoader:
    """
    Loads world data from a user-provided document (any format) or falls back to legacy hardcoded data.
    """
    def __init__(self, world_doc_path: Optional[str] = None):
        self.world_doc_path = world_doc_path

    def load(self) -> List[Era]:
        if self.world_doc_path:
            try:
                logger.info(f"Attempting to load world data from document: {self.world_doc_path}")
                schema = world_parser.WORLD_SCHEMA
                schema_dict = world_parser.parse_and_validate_world_document(self.world_doc_path, schema)
                eras = self._convert_schema_to_eras(schema_dict)
                logger.info("Successfully loaded world data from user document.")
                logger.debug(f"[World Data] Converted {len(eras)} eras from schema")
                for i, era in enumerate(eras):
                    logger.debug(f"[World Data] Era {i}: {era.name} - {len(era.archetypes)} archetypes")
                return eras
            except Exception as e:
                logger.error(f"Failed to load user world document: {e}. FALLBACK DISABLED - FAILING HARD.")
                # Log the specific error for debugging
                logger.debug(f"World document loading error details: {str(e)}", exc_info=True)
                raise Exception(f"World document parsing failed: {e}. Fallback disabled for debugging.") from e
        logger.info("Loading legacy hardcoded world data.")
        return get_legacy_world_data()

    def _convert_schema_to_eras(self, schema_dict: Dict[str, Any]) -> List[Era]:
        """
        Convert a validated schema dict (from AI) to a list of Era dataclasses.
        This is a placeholder; actual mapping logic depends on schema structure.
        """
        # Example: Assume schema_dict has a top-level 'eras' list
        eras = []
        for i, era_data in enumerate(schema_dict.get('eras', [])):
            era = Era(
                id=i,
                name=era_data.get('name', f'Era {i}'),
                description=era_data.get('description', ''),
                technologies=[Technology(**t) for t in era_data.get('technologies', [])],
                factions=[Faction(**f) for f in era_data.get('factions', [])],
                archetypes=[CharacterArchetype(**a) for a in era_data.get('archetypes', [])],
                plot_seeds=[PlotSeed(**p) for p in era_data.get('plot_seeds', [])],
            )
            eras.append(era)
        # If schema is flat (single era), create one Era
        if not eras and schema_dict.get('world_name'):
            era = Era(
                id=0,
                name=schema_dict.get('world_name', 'World Era'),
                description=schema_dict.get('description', ''),
                technologies=[Technology(name=t, description='', era=0, impact='') for t in schema_dict.get('technology', [])],
                factions=[],
                archetypes=[],
                plot_seeds=[],
            )
            eras.append(era)
        return eras

def get_legacy_world_data() -> List[Era]:
    """
    Returns the legacy hardcoded world data (unchanged).
    """
    # --- Era 0: Tipping Point (2025–2032) ---
    era0_technologies = [
        Technology(
            name="Prototype Presence Pods",
            description="Early, experimental versions of immersive, sense-attuned chambers used in grassroots mindfulness labs.",
            era=0,
            impact="Showed potential for guiding users into deep states of empathy and present-moment awareness, laying the groundwork for the Accord of Oneness."
        ),
        Technology(
            name="Community Microgrids",
            description="Localized, decentralized energy systems that can operate independently from the traditional grid.",
            era=0,
            impact="Increased local resilience against widespread power outages caused by climate instability and social disruption."
        ),
        Technology(
            name="Early Emotional AI (e-AI)",
            description="The first generation of LLMs trained on multimodal emotional datasets, used to assist in Pod facilitation.",
            era=0,
            impact="Enabled more adaptive and personalized experiences in prototype Pods, but raised early ethical questions about AI in mental health."
        ),
        Technology(
            name="Open-Source Climate Models",
            description="Citizen-led projects to create transparent, verifiable climate prediction models.",
            era=0,
            impact="Helped local communities prepare for severe climate events, fostering trust in science outside of institutional control."
        ),
        Technology(
            name="Vertical Farming",
            description="The practice of growing crops in vertically stacked layers, often in controlled, indoor environments.",
            era=0,
            impact="Improved food security in urban centers facing supply chain disruptions."
        ),
    ]

    era0_factions = [
        Faction(
            name="Community Resilience Networks",
            description="Grassroots organizations focused on building local resilience through mutual aid, skill-sharing, and the deployment of open-source, sustainable technologies.",
            values=["Solidarity", "Self-sufficiency", "Open-source principles", "Decentralization"],
            technologies=["Community Microgrids", "Vertical Farming", "Open-Source Climate Models"]
        ),
        Faction(
            name="Mindfulness Innovators",
            description="Decentralized groups of scientists, engineers, and spiritual practitioners experimenting with early-stage neuro-tech and contemplative practices.",
            values=["Mindful technology", "Inner exploration", "Empathy", "Cognitive liberty"],
            technologies=["Prototype Presence Pods", "Early Emotional AI (e-AI)"]
        ),
    ]

    era0_archetypes = [
        CharacterArchetype(
            name="Pod Pioneer",
            description="A scientist-mystic bridging neural technology and contemplative traditions, often working in a grassroots lab.",
            typical_traits=["Inquisitive", "Spiritual", "Tech-savvy", "Idealistic"],
            common_factions=["Mindfulness Innovators"]
        ),
        CharacterArchetype(
            name="Community Organizer",
            description="A local leader building resilience networks and deploying sustainable tech in their neighborhood.",
            typical_traits=["Pragmatic", "Connector", "Resourceful", "Hopeful"],
            common_factions=["Community Resilience Networks"]
        ),
    ]

    era0_plot_seeds = [
        PlotSeed(
            premise="A community's microgrid is sabotaged during a heatwave, forcing them to rely on mutual aid and low-tech solutions.",
            themes=["Resilience", "Community", "Sabotage", "Climate crisis"],
            potential_conflicts=["External sabotage vs. internal paranoia", "Resource scarcity vs. solidarity"]
        ),
        PlotSeed(
            premise="A Pod Pioneer has a breakthrough experience in their prototype Pod but struggles to explain its significance to a skeptical world.",
            themes=["Discovery", "Communication", "Inner vs. outer worlds", "Hope"],
            potential_conflicts=["Profound insight vs. inability to communicate it", "Fear of new technology"]
        ),
    ]

    # --- Era 1: Extinction Burst (2033–2047) ---
    era1_technologies = [
        Technology(
            name="Open-Source Presence Pods",
            description="The original, expensive Pod designs are reverse-engineered and released as open-source blueprints, making them accessible globally.",
            era=1,
            impact="Democratized access to transformative technology, but also led to unregulated, sometimes dangerous, homemade variants."
        ),
        Technology(
            name="Data & Water Scarcity Tech",
            description="Aggressive, often proprietary, technologies for data mining and water reclamation, deployed by patriarchal holdouts.",
            era=1,
            impact="Fueled the 'scarcity wars' as institutions tried to control essential resources."
        ),
        Technology(
            name="Disinformation AI",
            description="AI systems designed to spread misinformation and propaganda against Pods and decentralized movements.",
            era=1,
            impact="Increased social polarization and made it difficult to distinguish truth from manipulation."
        ),
    ]

    era1_factions = [
        Faction(
            name="Patriarchal Holdouts ('Iron Fathers')",
            description="Remnants of old, hierarchical institutions attempting to preserve control through resource hoarding and disinformation.",
            values=["Control", "Hierarchy", "Scarcity mindset", "Techno-solutionism"],
            technologies=["Data & Water Scarcity Tech", "Disinformation AI"]
        ),
    ]

    era1_archetypes = [
        CharacterArchetype(
            name="Iron Father Defector",
            description="An insider from a patriarchal institution who begins to question their indoctrination after a profound experience, often involving a Pod.",
            typical_traits=["Conflicted", "Brave", "Wary", "Seeking truth"],
            common_factions=["Patriarchal Holdouts ('Iron Fathers')"]
        ),
        CharacterArchetype(
            name="Mesh Runner",
            description="A courier who travels between isolated communities to physically deliver open-source Pod blueprints and maintain early, fragile communication networks.",
            typical_traits=["Resilient", "Nomadic", "Connector", "Stealthy"],
            common_factions=[]
        ),
    ]

    era1_plot_seeds = [
        PlotSeed(
            premise="An Iron Father Defector must smuggle open-source Pod blueprints out of a corporate enclave before they are destroyed.",
            themes=["Defection", "Risk", "Information liberation"],
            potential_conflicts=["Loyalty vs. morality", "Personal safety vs. the greater good"]
        ),
        PlotSeed(
            premise="A Mesh Runner's route is compromised, and they must find a new way to connect two communities that are being turned against each other by Disinformation AI.",
            themes=["Connection", "Truth vs. lies", "Overcoming division"],
            potential_conflicts=["Physical danger vs. the threat of misinformation"]
        ),
    ]

    # --- Assemble Eras ---
    era0 = Era(
        id=0,
        name="Tipping Point",
        description="Compounded AI disruption, severe climate events, social polarisation. Grassroots mindfulness labs experiment with early Pods.",
        technologies=era0_technologies,
        factions=era0_factions,
        archetypes=era0_archetypes,
        plot_seeds=era0_plot_seeds
    )

    era1 = Era(
        id=1,
        name="Extinction Burst",
        description="Old patriarchal institutions tighten control; \"scarcity wars\" over data & water. Prototype Pods prove transformative, spreading via open-source blueprints.",
        technologies=era1_technologies,
        factions=era1_factions,
        archetypes=era1_archetypes,
        plot_seeds=era1_plot_seeds
    )

    world_data = [era0, era1]
    
    # Validate the world data on load
    try:
        from src.validation import validate_world_data_with_logging
        validate_world_data_with_logging(world_data)
    except ImportError:
        logger.warning("Validation module not available, skipping world data validation")
    except Exception as e:
        logger.error(f"Error during world data validation: {e}")
    
    return world_data 

@handle_errors(
    category=ErrorCategory.CRITICAL,
    severity=ErrorSeverity.CRITICAL,
    user_message="Failed to load world data. The application cannot function without world-building information."
)
def get_world_data(world_doc_path: Optional[str] = None) -> List[Era]:
    """
    Unified entry point for loading world data.
    If world_doc_path is provided, attempts to load from user document; otherwise uses legacy data.
    """
    loader = WorldDataLoader(world_doc_path)
    return loader.load()

# --- Legacy data implementation ---
def _legacy_get_world_data_impl() -> List[Era]:
    # ... (Paste the full legacy get_world_data() code here) ...
    # For brevity, this is omitted in this snippet.
    pass 