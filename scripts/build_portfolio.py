from __future__ import annotations

import html
import json
import shutil
import textwrap
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable
from urllib.parse import quote

import fitz
from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = Path.home() / "Downloads"

PDF_OUTPUT = ROOT / "pdfs" / "source"
FILE_OUTPUT = ROOT / "files" / "source"
THUMB_OUTPUT = ROOT / "images" / "thumbnails"
PREVIEW_OUTPUT = ROOT / "images" / "previews"
PROJECT_OUTPUT = ROOT / "projects"
DOCS_OUTPUT = ROOT / "docs"
DATA_OUTPUT = ROOT / "data"

CARD_CANVAS = (1200, 1500)
PROJECT_SECTION_ORDER = ("Professional Work", "Academic Work")


@dataclass(frozen=True)
class SourceFile:
    kind: str
    path: Path
    member: str | None = None

    @property
    def display_name(self) -> str:
        return Path(self.member).name if self.member else self.path.name

    @property
    def origin_label(self) -> str:
        if self.member:
            return self.path.name
        return "Downloads"


@dataclass(frozen=True)
class DocumentSpec:
    key: str
    label: str
    summary: str
    sources: tuple[SourceFile, ...]


@dataclass(frozen=True)
class PreviewSpec:
    document_key: str
    page: int
    caption: str


@dataclass(frozen=True)
class ProjectSpec:
    id: str
    slug: str
    title: str
    subtitle: str
    category: str
    discipline: str
    work_stream: str
    reference: str
    authorship: str
    source_batch: str
    tags: tuple[str, ...]
    summary: str
    role: str
    scope: tuple[str, ...]
    deliverables: tuple[str, ...]
    main_document_key: str
    documents: tuple[DocumentSpec, ...]
    previews: tuple[PreviewSpec, ...]


@dataclass(frozen=True)
class LibraryFileSpec:
    title: str
    summary: str
    source: SourceFile
    file_type: str
    work_stream: str
    source_batch: str


@dataclass(frozen=True)
class ArchiveSpec:
    title: str
    source: SourceFile
    summary: str


def download_source(filename: str) -> SourceFile:
    return SourceFile("path", DOWNLOADS / filename)


def archive_source(archive_name: str, member: str) -> SourceFile:
    return SourceFile("zip", DOWNLOADS / archive_name, member)


def ensure_directory(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_text(path: Path, content: str) -> None:
    ensure_directory(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_font(size: int) -> ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def save_image(image: Image.Image, path: Path, quality: int = 92) -> None:
    ensure_directory(path)
    image.save(path, optimize=True, quality=quality)


def render_pdf_page(path: Path, page_number: int, scale: float = 2.0) -> Image.Image:
    with fitz.open(path) as document:
        page = document.load_page(page_number - 1)
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        return Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)


def fit_preview(image: Image.Image, width: int = 1800) -> Image.Image:
    target_height = int(image.height * (width / image.width))
    return image.resize((width, target_height), Image.Resampling.LANCZOS)


def build_card_thumbnail(image: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", CARD_CANVAS, "#ede9e1")
    margin = 90
    inner_size = (CARD_CANVAS[0] - margin * 2, CARD_CANVAS[1] - margin * 2)
    page = ImageOps.contain(image, inner_size)
    frame = Image.new("RGB", inner_size, "white")
    frame.paste(page, ((inner_size[0] - page.width) // 2, (inner_size[1] - page.height) // 2))
    canvas.paste(frame, (margin, margin))

    draw = ImageDraw.Draw(canvas)
    draw.rectangle((margin, margin, CARD_CANVAS[0] - margin, CARD_CANVAS[1] - margin), outline="#d4cec2", width=3)
    draw.rectangle(
        (margin + 16, margin + 16, CARD_CANVAS[0] - margin - 16, CARD_CANVAS[1] - margin - 16),
        outline="#ebe6db",
        width=1,
    )
    label = "DOCUMENT SET"
    font = load_font(18)
    text_box = draw.textbbox((0, 0), label, font=font)
    text_width = text_box[2] - text_box[0]
    text_height = text_box[3] - text_box[1]
    draw.rectangle((margin + 22, margin + 22, margin + 22 + text_width + 28, margin + 22 + text_height + 16), fill="#243a4b")
    draw.text((margin + 36, margin + 30), label, font=font, fill="#f7f4ee")
    return canvas


def url_for(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    return quote(relative, safe="/-_.()")


def page_count(path: Path) -> int:
    with fitz.open(path) as document:
        return document.page_count


def materialize_source(source: SourceFile, destination_dir: Path) -> Path:
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination_path = destination_dir / source.display_name

    if source.kind == "path":
        if not source.path.exists():
            raise FileNotFoundError(source.path)
        shutil.copy2(source.path, destination_path)
        return destination_path

    if source.kind == "zip":
        if source.member is None:
            raise ValueError("Zip sources require a member path.")
        with zipfile.ZipFile(source.path) as archive:
            ensure_directory(destination_path)
            with archive.open(source.member) as zipped_file, destination_path.open("wb") as output:
                shutil.copyfileobj(zipped_file, output)
        return destination_path

    raise ValueError(f"Unsupported source kind: {source.kind}")


def strip_margin(text: str) -> str:
    return textwrap.dedent(text).strip()


PROJECTS = (
    ProjectSpec(
        id="c8676",
        slug="temporary-works-c8676",
        title="Temporary Works Packages for Site Accommodation",
        subtitle="Cabin bases, Heras fencing and scaffold mat checks",
        category="Professional",
        discipline="Temporary Works",
        work_stream="Professional Work",
        reference="C8676",
        authorship="Professional issue packs",
        source_batch="Direct PDF set",
        tags=("Professional", "Temporary Works", "Foundations", "Wind Loading"),
        summary=(
            "Temporary works calculation packs covering stacked site cabin bases, Heras fencing, "
            "and scaffold mat design for site accommodation."
        ),
        role=(
            "Preparation of temporary works calculations covering load assessment, wind actions, "
            "bearing checks, and supporting technical sketches."
        ),
        scope=(
            "Cabin base checks using supplier information and bearing arrangements.",
            "Temporary fencing stability checks under wind loading.",
            "Scaffold sole board and mat support checks for temporary works loading.",
        ),
        deliverables=(
            "Issued calculation packs for cabin bases, fencing, and scaffold support arrangements.",
            "Wind loading, bearing, and temporary works design checks.",
            "Supporting preview pages and direct access to the full document set.",
        ),
        main_document_key="cabin-bases",
        documents=(
            DocumentSpec(
                key="cabin-bases",
                label="Calculations 01-09",
                summary="Cabin-base calculation pack for stacked site accommodation foundations.",
                sources=(
                    download_source("C8676 - Calculations 01 - 09 inc.pdf"),
                    download_source("C8676 - Calculations 01 - 09 inc (1).pdf"),
                ),
            ),
            DocumentSpec(
                key="heras-fencing",
                label="Calculations H01-H05",
                summary="Temporary fencing calculation pack covering stability under wind loading.",
                sources=(download_source("C8676 Calculations - H01-H05 inc.pdf"),),
            ),
            DocumentSpec(
                key="scaffold-mat",
                label="Calculations S01-S02",
                summary="Scaffold mat and sole-board support calculations for temporary works loading.",
                sources=(download_source("c8676 Calculations S01 - S02 inc.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("cabin-bases", 1, "Cabin-base package cover sheet."),
            PreviewSpec("cabin-bases", 2, "Representative calculation page from the cabin-base package."),
            PreviewSpec("heras-fencing", 1, "Heras fencing package cover sheet."),
            PreviewSpec("scaffold-mat", 1, "Scaffold mat package cover sheet."),
        ),
    ),
    ProjectSpec(
        id="c8765",
        slug="classroom-foundation-design-c8765",
        title="Classroom Foundation Design",
        subtitle="Salisbury Road Primary School, Plymouth",
        category="Professional",
        discipline="Foundations",
        work_stream="Professional Work",
        reference="C8765",
        authorship="Professional calculation pack and supporting sheets",
        source_batch="attachments.zip",
        tags=("Professional", "Foundations", "Education", "Timber"),
        summary=(
            "Foundation design package for a timber-frame classroom building at Salisbury Road Primary School, "
            "supported by calculation sheets and associated drawing information."
        ),
        role=(
            "Preparation of the structural calculations and supporting technical sheets for the classroom "
            "foundation arrangement."
        ),
        scope=(
            "Foundation design for a timber-frame classroom building.",
            "Bearing and foundation strategy development informed by site investigation information.",
            "Supporting technical sheets and drawings issued alongside the calculation pack.",
        ),
        deliverables=(
            "Main calculation pack covering the classroom foundation design.",
            "Supporting drawing sheets issued with the calculation package.",
            "Preview pages and direct access to the full document set.",
        ),
        main_document_key="calc-pack",
        documents=(
            DocumentSpec(
                key="calc-pack",
                label="Calculations 01-24",
                summary="Main calculation pack for the classroom foundation design.",
                sources=(archive_source("attachments.zip", "C8765. Calculations 01 - 24 inc.pdf"),),
            ),
            DocumentSpec(
                key="sheet-01",
                label="Sheet 01",
                summary="Supporting drawing sheet issued with the classroom foundation package.",
                sources=(archive_source("attachments.zip", "C8765-01.pdf"),),
            ),
            DocumentSpec(
                key="sheet-02",
                label="Sheet 02",
                summary="Supporting drawing sheet issued with the classroom foundation package.",
                sources=(archive_source("attachments.zip", "C8765-02.pdf"),),
            ),
            DocumentSpec(
                key="sheet-03",
                label="Sheet 03",
                summary="Supporting drawing sheet issued with the classroom foundation package.",
                sources=(archive_source("attachments.zip", "C8765-03.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("calc-pack", 1, "Project data sheet for the classroom foundation package."),
            PreviewSpec("calc-pack", 2, "Representative internal page from the foundation calculations."),
            PreviewSpec("sheet-01", 1, "Supporting drawing sheet from the package."),
        ),
    ),
    ProjectSpec(
        id="c8611",
        slug="school-extension-foundation-design-c8611",
        title="School Extension Foundation Design",
        subtitle="Diptford Primary School",
        category="Professional",
        discipline="Foundations",
        work_stream="Professional Work",
        reference="C8611",
        authorship="Professional calculation pack",
        source_batch="attachments.zip",
        tags=("Professional", "Foundations", "Education"),
        summary=(
            "Foundation design package for a classroom extension at Diptford Primary School, using a "
            "reinforced beam and piles solution."
        ),
        role=(
            "Preparation of the structural calculation package for the extension foundation design."
        ),
        scope=(
            "Foundation design for a school extension classroom.",
            "Beam-and-piles foundation strategy supported by site investigation information.",
            "Technical calculation sheets issued for authority and project review.",
        ),
        deliverables=(
            "Foundation calculation pack for the extension works.",
            "Supporting design information for the selected beam-and-piles approach.",
            "Preview pages and full in-browser access to the document.",
        ),
        main_document_key="calc-pack",
        documents=(
            DocumentSpec(
                key="calc-pack",
                label="Calculations 01-14",
                summary="Foundation design calculation pack for the Diptford Primary School extension.",
                sources=(archive_source("attachments.zip", "C8611. Calculations - 01 - 14 inc_compressed.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("calc-pack", 1, "Project data sheet for the school extension foundation design."),
            PreviewSpec("calc-pack", 2, "Representative internal calculation page."),
            PreviewSpec("calc-pack", 3, "Additional calculation content from the foundation package."),
        ),
    ),
    ProjectSpec(
        id="c8030",
        slug="flat-roof-installation-c8030",
        title="Flat Roof Installation and Alterations",
        subtitle="Manor Corner, Paignton",
        category="Professional",
        discipline="Roof Structures",
        work_stream="Professional Work",
        reference="C8030",
        authorship="Professional proposal set",
        source_batch="attachments (1).zip",
        tags=("Professional", "Commercial", "Roof Structures", "Timber", "Steelwork"),
        summary=(
            "Proposal package for structural alterations and the installation of a new flat roof to an "
            "existing commercial building at Manor Corner, Paignton."
        ),
        role=(
            "Preparation of the proposal set covering the roof alterations, structural support strategy, "
            "and technical presentation of the scheme."
        ),
        scope=(
            "New flat-roof installation to an existing commercial building.",
            "Use of timber, steel, and proprietary joist components within the altered roof structure.",
            "Proposal sheets issued to communicate the structural approach.",
        ),
        deliverables=(
            "Proposal set covering the altered roof structure.",
            "Supporting structural information for timber and steel roof elements.",
            "Preview pages and direct access to the full proposal package.",
        ),
        main_document_key="proposal-pack",
        documents=(
            DocumentSpec(
                key="proposal-pack",
                label="Proposals R01-R22",
                summary="Proposal set for the new flat-roof installation at Manor Corner.",
                sources=(archive_source("attachments (1).zip", "C8030. Proposals R01 - R22 inc_compressed.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("proposal-pack", 1, "Project data sheet for the Manor Corner proposal set."),
            PreviewSpec("proposal-pack", 2, "Representative internal page from the roof proposal package."),
            PreviewSpec("proposal-pack", 3, "Additional proposal sheet from the document set."),
        ),
    ),
    ProjectSpec(
        id="c8839",
        slug="internal-alterations-and-deck-design-c8839",
        title="Internal Alterations and Deck Design",
        subtitle="Mariners, Heath Road, Brixham",
        category="Professional",
        discipline="Structural Alterations",
        work_stream="Professional Work",
        reference="C8839",
        authorship="Professional calculation pack",
        source_batch="attachments (1).zip",
        tags=("Professional", "Residential", "Alterations", "Steelwork", "Timber"),
        summary=(
            "Structural calculation package for residential internal alterations and deck design at "
            "Mariners, Heath Road, Brixham."
        ),
        role=(
            "Preparation of the structural calculations covering the alteration works and the deck design package."
        ),
        scope=(
            "Residential internal alterations and associated deck design.",
            "Steel and timber structural checks within the altered arrangement.",
            "Issued calculation sheets supporting the proposed works.",
        ),
        deliverables=(
            "Main calculation pack for the alteration and deck design works.",
            "Supporting structural checks and technical issue sheets.",
            "Preview pages and direct access to the full package.",
        ),
        main_document_key="calc-pack",
        documents=(
            DocumentSpec(
                key="calc-pack",
                label="Calculations 01-51",
                summary="Calculation pack for internal alterations and deck design at Mariners.",
                sources=(archive_source("attachments (1).zip", "C8839. Calculation pack 01 - 51inc_compressed.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("calc-pack", 1, "Project data sheet for the Mariners calculation package."),
            PreviewSpec("calc-pack", 2, "Representative internal page from the calculation pack."),
            PreviewSpec("calc-pack", 3, "Additional calculation content from the document set."),
        ),
    ),
    ProjectSpec(
        id="c8829",
        slug="temporary-works-noss-on-dart-c8829",
        title="Temporary Works Packages for Noss on Dart Marina",
        subtitle="Piling platforms, scaffold systems, crane base and retaining wall",
        category="Professional",
        discipline="Temporary Works",
        work_stream="Professional Work",
        reference="C8829",
        authorship="Professional temporary works packages",
        source_batch="attachments (2).zip",
        tags=("Professional", "Temporary Works", "Foundations", "Retaining Structures", "Marine"),
        summary=(
            "Coordinated temporary works packages for Noss on Dart Marina covering piling platforms, "
            "scaffold and falsework spreaders, a tower crane base, and a king post retaining wall."
        ),
        role=(
            "Preparation of multiple temporary works calculation packages across the marina development, "
            "covering platform design, scaffold support arrangements, crane base checks, and retaining wall design."
        ),
        scope=(
            "Granular working platforms for piling plant.",
            "Scaffold and falsework spreaders for access and support arrangements.",
            "Tower crane base and king post retaining wall packages within the wider temporary works set.",
        ),
        deliverables=(
            "Seven temporary works document sets under the same project reference.",
            "Packages covering platforms, spreaders, scaffold systems, crane base, and retaining wall design.",
            "Preview pages and direct access to the full grouped document set.",
        ),
        main_document_key="g-pack",
        documents=(
            DocumentSpec(
                key="g-pack",
                label="Calculations G01-G32",
                summary="Granular working-platform calculations for the GEAX EK60L piling rig.",
                sources=(archive_source("attachments (2).zip", "C8829 Calculations G01 - G32 inc.pdf"),),
            ),
            DocumentSpec(
                key="p-pack",
                label="Calculations P01-P32",
                summary="Granular working-platform calculations for the Casagrande B175XP CFA piling rig.",
                sources=(archive_source("attachments (2).zip", "C8829. Calculations P01 - P32 inc_compressed.pdf"),),
            ),
            DocumentSpec(
                key="cp-pack",
                label="CP1-CP5",
                summary="Cantilevered platform scaffold calculations for roof-access support.",
                sources=(archive_source("attachments (2).zip", "C8829 CP1 - CP5 inc.pdf"),),
            ),
            DocumentSpec(
                key="s-pack",
                label="S01-S06",
                summary="Prop spreader calculations for apartment-block falsework support to the undercroft.",
                sources=(archive_source("attachments (2).zip", "C8829. Calculations S01 - S06 incl..pdf"),),
            ),
            DocumentSpec(
                key="f-pack",
                label="F01-F02",
                summary="Foundation scaffold spreader package for bridged access scaffolding.",
                sources=(archive_source("attachments (2).zip", "C8829 Calculation packF01 - F02 inc.pdf"),),
            ),
            DocumentSpec(
                key="tc-pack",
                label="TC01-TC08",
                summary="Tower crane base calculations for the Comansa 16 LC 260 foundation.",
                sources=(archive_source("attachments (2).zip", "C8829. Calculations TC01-TC08 inc.pdf"),),
            ),
            DocumentSpec(
                key="k-pack",
                label="K01-K14",
                summary="King post retaining wall calculations for the eastern boundary.",
                sources=(archive_source("attachments (2).zip", "C8829. K01 - K14 inc Calculations_compressed.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("g-pack", 1, "Project data sheet for the GEAX EK60L piling-platform package."),
            PreviewSpec("p-pack", 1, "Project data sheet for the Casagrande B175XP CFA platform package."),
            PreviewSpec("tc-pack", 1, "Project data sheet for the tower crane base package."),
            PreviewSpec("k-pack", 1, "Project data sheet for the king post retaining wall package."),
        ),
    ),
    ProjectSpec(
        id="c8758",
        slug="commercial-alterations-c8758",
        title="Commercial Alterations to Existing Building",
        subtitle="Extension to Riviera Sports Bar, Torquay",
        category="Professional",
        discipline="Structural Alterations",
        work_stream="Professional Work",
        reference="C8758",
        authorship="Professional calculation pack",
        source_batch="attachments (3).zip",
        tags=("Professional", "Commercial", "Alterations", "Steelwork", "Timber"),
        summary=(
            "Structural calculation package for alterations to the existing Riviera Sports Bar building "
            "in Torquay."
        ),
        role=(
            "Preparation of the structural calculations for the alteration works to the existing commercial building."
        ),
        scope=(
            "Structural alterations to an existing commercial building.",
            "Use of steel, timber, and masonry elements within the proposed works.",
            "Issued calculation sheets supporting the extension and alteration package.",
        ),
        deliverables=(
            "Calculation pack covering the building alterations.",
            "Supporting structural checks for the proposed works.",
            "Preview pages and direct access to the full document set.",
        ),
        main_document_key="calc-pack",
        documents=(
            DocumentSpec(
                key="calc-pack",
                label="Calculations 01-28",
                summary="Calculation pack for the Riviera Sports Bar alteration works.",
                sources=(archive_source("attachments (3).zip", "C8758 Calculations_compressed.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("calc-pack", 1, "Project data sheet for the Riviera Sports Bar calculation package."),
            PreviewSpec("calc-pack", 2, "Representative internal page from the alteration package."),
            PreviewSpec("calc-pack", 3, "Additional calculation content from the document set."),
        ),
    ),
    ProjectSpec(
        id="c8707",
        slug="merchants-loft-alterations-c8707",
        title="Internal Alterations and Temporary Works Propping",
        subtitle="The Merchants Loft, Pump Street, Brixham",
        category="Professional",
        discipline="Structural Alterations",
        work_stream="Professional Work",
        reference="C8707",
        authorship="Professional calculation packs",
        source_batch="attachments (3).zip",
        tags=("Professional", "Residential", "Alterations", "Temporary Works"),
        summary=(
            "Paired calculation packs for The Merchants Loft covering the permanent internal alterations "
            "and the temporary works propping required to support the works."
        ),
        role=(
            "Preparation of the structural calculations for the permanent alterations together with the "
            "temporary works propping package."
        ),
        scope=(
            "Permanent structural alterations to an existing residential building.",
            "Temporary works propping to support the alteration sequence.",
            "Issued calculation sheets covering both permanent and temporary conditions.",
        ),
        deliverables=(
            "Main structural calculation pack for the alteration works.",
            "Temporary works propping package issued under the same project reference.",
            "Preview pages and direct access to the full document set.",
        ),
        main_document_key="main-pack",
        documents=(
            DocumentSpec(
                key="main-pack",
                label="Calculations 01-24",
                summary="Main structural calculation pack for the internal alteration works.",
                sources=(archive_source("attachments (3).zip", "C8707. Calculations 01 - 24 inc_compressed.pdf"),),
            ),
            DocumentSpec(
                key="t-pack",
                label="Calcs T01-T08",
                summary="Temporary works propping calculations issued for the same project.",
                sources=(archive_source("attachments (3).zip", "C8707.  Calcs . T01 - T08 inc.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("main-pack", 1, "Project data sheet for the main alteration package."),
            PreviewSpec("main-pack", 2, "Representative internal page from the alteration calculations."),
            PreviewSpec("t-pack", 1, "Project data sheet for the temporary works propping package."),
        ),
    ),
    ProjectSpec(
        id="monitoring-coursework",
        slug="deformation-monitoring-coursework",
        title="Deformation Monitoring Coursework",
        subtitle="Surveying coursework for monitoring a museum during adjacent tunnelling",
        category="Academic",
        discipline="Surveying",
        work_stream="Academic Work",
        reference="AR10368",
        authorship="Individual coursework submission",
        source_batch="attachments (4).zip",
        tags=("Academic", "Surveying", "Monitoring"),
        summary=(
            "University of Bath surveying coursework focused on deformation monitoring for the Holburne Museum "
            "during proposed tunnelling works."
        ),
        role="Individual coursework submission covering monitoring strategy, survey control, and movement assessment for a tunnelling scenario.",
        scope=(
            "Monitoring requirements for a building affected by nearby tunnelling.",
            "Survey control, observations, and movement tracking considerations.",
            "Technical coursework presentation for a civil engineering surveying module.",
        ),
        deliverables=(
            "Coursework report setting out the monitoring approach.",
            "Supporting technical discussion of control, observations, and movement assessment.",
            "Preview pages and in-browser access to the full submission.",
        ),
        main_document_key="monitoring-pdf",
        documents=(
            DocumentSpec(
                key="monitoring-pdf",
                label="219326201_Monitoring.pdf",
                summary="Coursework report covering deformation monitoring for a tunnelling scenario.",
                sources=(archive_source("attachments (4).zip", "219326201_Monitoring.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("monitoring-pdf", 1, "Coursework cover page and brief."),
            PreviewSpec("monitoring-pdf", 2, "Monitoring strategy content from the submission."),
        ),
    ),
    ProjectSpec(
        id="timber-masonry-coursework",
        slug="timber-masonry-coursework",
        title="Timber and Masonry Coursework",
        subtitle="Structural design and construction coursework",
        category="Academic",
        discipline="Structural Design",
        work_stream="Academic Work",
        reference="AR20442",
        authorship="Individual coursework submission",
        source_batch="attachments (4).zip",
        tags=("Academic", "Structural", "Timber", "Masonry"),
        summary=(
            "University coursework submitted under AR20442: Structural Design and Construction, "
            "covering timber and masonry design in a longer-form technical submission."
        ),
        role="Individual coursework submission covering structural design calculations, detailing considerations, and technical presentation.",
        scope=(
            "Timber and masonry structural design coursework.",
            "Extended report format covering the full design submission.",
            "Academic presentation of design calculations and supporting notes.",
        ),
        deliverables=(
            "Merged coursework report covering the design submission.",
            "Supporting calculation pages and technical narrative.",
            "Preview pages and in-browser access to the full report.",
        ),
        main_document_key="timber-masonry-pdf",
        documents=(
            DocumentSpec(
                key="timber-masonry-pdf",
                label="courseowk timber _merged.pdf",
                summary="Coursework report covering timber and masonry design.",
                sources=(archive_source("attachments (4).zip", "courseowk timber _merged.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("timber-masonry-pdf", 1, "Coursework cover page."),
            PreviewSpec("timber-masonry-pdf", 2, "Opening coursework content page."),
            PreviewSpec("timber-masonry-pdf", 6, "Representative internal page from the submission."),
        ),
    ),
    ProjectSpec(
        id="lc3-report",
        slug="lc3-technical-report",
        title="LC3 Technical Report",
        subtitle="Assessment of limestone calcined clay cement for low-carbon concrete construction",
        category="Academic",
        discipline="Materials / Concrete",
        work_stream="Academic Work",
        reference="LC3 report",
        authorship="Individual technical report",
        source_batch="uniwork.zip",
        tags=("Academic", "Materials", "Concrete", "Sustainability"),
        summary=(
            "Technical report assessing LC3, its raw materials, production process, hydration behaviour, "
            "and use in lower-carbon concrete construction."
        ),
        role="Individual technical report assessing LC3 as a lower-carbon concrete material.",
        scope=(
            "Materials assessment focused on LC3 as a lower-carbon cement system.",
            "Review of production, hydration, and construction implications.",
            "Structured technical report covering materials behaviour and construction implications.",
        ),
        deliverables=(
            "Technical report on LC3 and its application in lower-carbon concrete construction.",
            "Review of raw materials, production, hydration, and construction implications.",
            "Preview pages and in-browser access to the full report.",
        ),
        main_document_key="lc3-pdf",
        documents=(
            DocumentSpec(
                key="lc3-pdf",
                label="DH_LC3_COURSEWORK.pdf",
                summary="Technical report assessing LC3 for lower-carbon concrete construction.",
                sources=(archive_source("uniwork.zip", "DH_LC3_COURSEWORK.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("lc3-pdf", 1, "Report cover page."),
            PreviewSpec("lc3-pdf", 2, "Opening technical content page."),
            PreviewSpec("lc3-pdf", 5, "Representative internal page from the report."),
        ),
    ),
    ProjectSpec(
        id="the-sty",
        slug="the-sty-group-6",
        title="The Sty",
        subtitle="Group 6 structural scheme submission for a pool and Pilates building",
        category="Academic",
        discipline="Structural Design",
        work_stream="Academic Work",
        reference="Group 6",
        authorship="Group submission",
        source_batch="uniwork.zip",
        tags=("Academic", "Structural", "Timber", "Group Work"),
        summary=(
            "Group 6 submission for a proposed pool and Pilates building. The opening pages set out the "
            "site context, concept, and structural scheme, including curved timber beams and CLT floor elements."
        ),
        role="Group design submission with Daniel contributing to the engineering development and technical presentation of the scheme.",
        scope=(
            "Structural scheme development for a building proposal in the New Forest.",
            "Concept and structural overview pages covering long-span timber elements.",
            "Group structural design submission combining concept development, structural framing, and presentation material.",
        ),
        deliverables=(
            "Group design submission for the proposed pool and Pilates building.",
            "Structural overview pages and supporting concept material.",
            "Preview pages and in-browser access to the full submission.",
        ),
        main_document_key="the-sty-pdf",
        documents=(
            DocumentSpec(
                key="the-sty-pdf",
                label="Final submission v4.pdf",
                summary="Group 6 submission covering the structural scheme for a pool and Pilates building.",
                sources=(archive_source("uniwork.zip", "Final submission v4.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("the-sty-pdf", 1, "Title page."),
            PreviewSpec("the-sty-pdf", 2, "Site location and architectural scheme page."),
            PreviewSpec("the-sty-pdf", 3, "Structural overview page."),
        ),
    ),
    ProjectSpec(
        id="aula-magna",
        slug="aula-magna-engineers-report",
        title="Aula Magna Engineers' Report",
        subtitle="Group 6 report for a regenerative peace-centre proposal",
        category="Academic",
        discipline="Structural / Environmental Design",
        work_stream="Academic Work",
        reference="Group 6",
        authorship="Group report",
        source_batch="uniwork.zip",
        tags=("Academic", "Structural", "Sustainability", "Group Work"),
        summary=(
            "Group 6 engineers' report for the Aula Magna proposal, with emphasis on regenerative design, "
            "low-carbon strategies, and the design development process."
        ),
        role="Group engineers' report with Daniel contributing to the engineering narrative and technical presentation of the proposal.",
        scope=(
            "Engineering report for a concept-led building proposal.",
            "Sustainability and environmental strategy content.",
            "Design progression and engineering narrative within a group report.",
        ),
        deliverables=(
            "Group engineers' report for the Aula Magna proposal.",
            "Engineering narrative, design progression, and supporting report material.",
            "Preview pages and in-browser access to the full report.",
        ),
        main_document_key="aula-magna-pdf",
        documents=(
            DocumentSpec(
                key="aula-magna-pdf",
                label="Group-06_Engineers_Report_25.pdf",
                summary="Group engineers' report for the Aula Magna proposal.",
                sources=(archive_source("uniwork.zip", "Group-06_Engineers_Report_25.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("aula-magna-pdf", 1, "Report cover page."),
            PreviewSpec("aula-magna-pdf", 2, "Opening project summary page."),
            PreviewSpec("aula-magna-pdf", 3, "Design progression page."),
        ),
    ),
    ProjectSpec(
        id="geotechnical-design",
        slug="geotechnical-design-group-3",
        title="Geotechnical Design Technical Report",
        subtitle="Aquae Sulis Music Venue foundation design study",
        category="Academic",
        discipline="Geotechnical Design",
        work_stream="Academic Work",
        reference="AR20478",
        authorship="Group technical report",
        source_batch="uniwork.zip",
        tags=("Academic", "Geotechnical", "Foundations", "Group Work"),
        summary=(
            "Group technical report examining ground conditions, foundation options, and geotechnical design "
            "considerations for the Aquae Sulis Music Venue."
        ),
        role=(
            "Group technical report with Daniel contributing to foundation strategy development, "
            "geotechnical assessment, and report presentation."
        ),
        scope=(
            "Foundation strategy and soil-mechanics study for the Aquae Sulis Music Venue project.",
            "Assessment of ground conditions, design parameters, and foundation approach.",
            "Technical report presenting the geotechnical basis of design.",
        ),
        deliverables=(
            "Geotechnical design report covering site assumptions, ground profile, and foundation recommendations.",
            "Supporting foundation-design narrative and technical presentation.",
            "Preview pages and in-browser access to the full report.",
        ),
        main_document_key="geotechnical-pdf",
        documents=(
            DocumentSpec(
                key="geotechnical-pdf",
                label="Geotechnical Design - Group 3.pdf",
                summary="Geotechnical design report for the Aquae Sulis Music Venue foundation study.",
                sources=(archive_source("uniwork.zip", "Geotechnical Design - Group 3.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("geotechnical-pdf", 1, "Report cover page."),
            PreviewSpec("geotechnical-pdf", 2, "Opening technical content page."),
            PreviewSpec("geotechnical-pdf", 4, "Representative internal page from the report."),
        ),
    ),
    ProjectSpec(
        id="gfrp-footbridge-fea",
        slug="gfrp-footbridge-fea",
        title="GFRP Footbridge FEA",
        subtitle="Group 4 finite element analysis brief",
        category="Academic",
        discipline="Structural Analysis",
        work_stream="Academic Work",
        reference="AR30400 Group 4",
        authorship="Group submission",
        source_batch="uniwork.zip",
        tags=("Academic", "Structural", "FEA", "Group Work"),
        summary=(
            "Group finite element analysis brief assessing the structural behaviour of a GFRP footbridge concept."
        ),
        role=(
            "Group FEA submission with Daniel contributing to modelling assumptions, results "
            "interpretation, and technical presentation."
        ),
        scope=(
            "Finite element analysis of a GFRP footbridge concept.",
            "Assessment of structural response using a concise analysis brief.",
            "Group submission combining modelling output and engineering commentary.",
        ),
        deliverables=(
            "Group finite element analysis brief for the footbridge study.",
            "Supporting structural response discussion and presentation of results.",
            "Preview pages and in-browser access to the full submission.",
        ),
        main_document_key="fea-pdf",
        documents=(
            DocumentSpec(
                key="fea-pdf",
                label="Group_4_FEA2024.pdf",
                summary="Group finite element analysis brief for the GFRP footbridge concept.",
                sources=(archive_source("uniwork.zip", "Group_4_FEA2024.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("fea-pdf", 1, "Report cover page."),
            PreviewSpec("fea-pdf", 2, "Opening analysis content page."),
        ),
    ),
    ProjectSpec(
        id="office-loading-dissertation",
        slug="office-loading-dissertation",
        title="Analysing Peak Loading Conditions in Office Environments",
        subtitle="MEng dissertation",
        category="Academic",
        discipline="Research",
        work_stream="Academic Work",
        reference="AR30315",
        authorship="Individual dissertation",
        source_batch="uniwork.zip",
        tags=("Academic", "Research", "Dissertation"),
        summary=(
            "MEng dissertation investigating peak loading conditions in office environments, with emphasis "
            "on occupancy loading behaviour and design implications."
        ),
        role="Individual dissertation investigating peak loading conditions in office environments.",
        scope=(
            "Research project examining peak loading conditions in office environments.",
            "Extended dissertation covering literature review, methodology, and findings.",
            "Technical discussion of loading behaviour and implications for design assumptions.",
        ),
        deliverables=(
            "Full dissertation document for the office-loading research study.",
            "Supporting research narrative, methodology, and technical discussion.",
            "Preview pages and in-browser access to the full dissertation.",
        ),
        main_document_key="dissertation-pdf",
        documents=(
            DocumentSpec(
                key="dissertation-pdf",
                label="Heard_D_diss_2024-25.pdf",
                summary="MEng dissertation on peak loading conditions in office environments.",
                sources=(archive_source("uniwork.zip", "Heard_D_diss_2024-25.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("dissertation-pdf", 1, "Dissertation title page."),
            PreviewSpec("dissertation-pdf", 2, "Opening dissertation content page."),
            PreviewSpec("dissertation-pdf", 4, "Representative internal page from the dissertation."),
        ),
    ),
    ProjectSpec(
        id="glastonbury-reservoir",
        slug="glastonbury-reservoir-proposal",
        title="Glastonbury Reservoir Proposal",
        subtitle="Group 7 infrastructure report",
        category="Academic",
        discipline="Water / Infrastructure",
        work_stream="Academic Work",
        reference="Group 7",
        authorship="Group report",
        source_batch="uniwork.zip",
        tags=("Academic", "Infrastructure", "Water", "Group Work"),
        summary=(
            "Group 7 report for a reservoir proposal, combining water-resilience, environmental, "
            "and infrastructure themes in a long-form academic submission."
        ),
        role="Group infrastructure report with Daniel contributing to the engineering narrative and report presentation.",
        scope=(
            "Reservoir proposal and wider water-resilience narrative.",
            "Infrastructure report format with environmental and strategic framing.",
            "Group infrastructure report combining engineering, environmental, and strategic planning material.",
        ),
        deliverables=(
            "Group infrastructure report for the reservoir proposal.",
            "Supporting environmental and strategic engineering narrative.",
            "Preview pages and in-browser access to the full report.",
        ),
        main_document_key="reservoir-pdf",
        documents=(
            DocumentSpec(
                key="reservoir-pdf",
                label="Report_Group_7 (1).pdf",
                summary="Group infrastructure report for the Glastonbury Reservoir proposal.",
                sources=(archive_source("uniwork.zip", "Report_Group_7 (1).pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("reservoir-pdf", 1, "Report cover page."),
            PreviewSpec("reservoir-pdf", 2, "Acknowledgements and report framing."),
            PreviewSpec("reservoir-pdf", 3, "Opening introduction page."),
        ),
    ),
    ProjectSpec(
        id="advanced-timber-connection-design",
        slug="advanced-timber-connection-design",
        title="Advanced Timber Engineering: Connection Design",
        subtitle="Connection design coursework",
        category="Academic",
        discipline="Timber Engineering",
        work_stream="Academic Work",
        reference="AR40418",
        authorship="Individual coursework submission",
        source_batch="uniwork.zip",
        tags=("Academic", "Timber", "Connection Design"),
        summary=(
            "Advanced timber engineering coursework covering the design and presentation of timber connection details."
        ),
        role="Individual coursework submission focused on timber connection design and technical presentation.",
        scope=(
            "Timber connection design exercise for an advanced timber engineering module.",
            "Connection detailing and supporting calculations presented in report form.",
            "Technical submission combining design checks and clear engineering presentation.",
        ),
        deliverables=(
            "Timber connection design coursework submission.",
            "Supporting technical pages covering the connection design exercise.",
            "Preview pages and in-browser access to the full submission.",
        ),
        main_document_key="advanced-timber-pdf",
        documents=(
            DocumentSpec(
                key="advanced-timber-pdf",
                label="TIMBER_CW_PDF.pdf",
                summary="Advanced timber engineering coursework covering timber connection design.",
                sources=(archive_source("uniwork.zip", "TIMBER_CW_PDF.pdf"),),
            ),
        ),
        previews=(
            PreviewSpec("advanced-timber-pdf", 1, "Coursework cover page."),
            PreviewSpec("advanced-timber-pdf", 2, "Opening coursework content page."),
            PreviewSpec("advanced-timber-pdf", 4, "Representative internal page from the submission."),
        ),
    ),
)


LIBRARY_FILES = (
    LibraryFileSpec(
        title="Structures Coursework Spreadsheet",
        summary="Spreadsheet submitted alongside the structures coursework set.",
        source=archive_source("uniwork.zip", "Structures_CW .xlsx"),
        file_type="xlsx",
        work_stream="Academic Work",
        source_batch="uniwork.zip",
    ),
)


ARCHIVES = (
    ArchiveSpec(
        title="Professional Document Bundle 01",
        source=download_source("attachments.zip"),
        summary="Archive containing additional professional calculation packs and supporting PDFs.",
    ),
    ArchiveSpec(
        title="Professional Document Bundle 02",
        source=download_source("attachments (1).zip"),
        summary="Archive containing additional professional proposal and calculation packs.",
    ),
    ArchiveSpec(
        title="Professional Document Bundle 03",
        source=download_source("attachments (2).zip"),
        summary="Archive containing the grouped C8829 temporary works packages.",
    ),
    ArchiveSpec(
        title="Professional Document Bundle 04",
        source=download_source("attachments (3).zip"),
        summary="Archive containing the C8758 and C8707 professional calculation packs.",
    ),
    ArchiveSpec(
        title="Academic Document Bundle 01",
        source=download_source("attachments (4).zip"),
        summary="Archive containing academic coursework submissions.",
    ),
    ArchiveSpec(
        title="Academic Document Bundle 02",
        source=download_source("uniwork.zip"),
        summary="Archive containing university reports, coursework, and dissertation material.",
    ),
)


def render_list(items: Iterable[str]) -> str:
    return "".join(f"<li>{html.escape(item)}</li>" for item in items)


def render_tags(tags: Iterable[str]) -> str:
    return "".join(f'<li class="tag">{html.escape(tag)}</li>' for tag in tags)


def render_meta_rows(project: dict) -> str:
    rows = (
        ("Reference", project["reference"]),
        ("Work type", project["category"]),
        ("Authorship", project["authorship"]),
        ("Discipline", project["discipline"]),
        ("Documents", str(len(project["documents"]))),
    )
    return "".join(f"<dt>{html.escape(label)}</dt><dd>{html.escape(value)}</dd>" for label, value in rows)


def render_alias_links(aliases: list[dict], root_prefix: str) -> str:
    if not aliases:
        return "None"
    links = [
        f'<a href="{root_prefix}{alias["url"]}" target="_blank" rel="noreferrer">{html.escape(alias["name"])}</a>'
        for alias in aliases
    ]
    return ", ".join(links)


def render_document_cards(documents: list[dict], root_prefix: str) -> str:
    cards: list[str] = []
    for index, document in enumerate(documents):
        alias_html = render_alias_links(document["aliases"], root_prefix)
        alias_block = ""
        if document["aliases"]:
            alias_block = strip_margin(
                f"""
                <p class="document-card__note">
                  Also supplied as: {alias_html}
                </p>
                """
            )
        cards.append(
            strip_margin(
                f"""
                <article class="document-card">
                  <div class="document-card__meta">
                    <span>{html.escape(document["label"])}</span>
                    <span>{document["page_count"]} pages</span>
                  </div>
                  <h3>{html.escape(document["file_name"])}</h3>
                  <p>{html.escape(document["summary"])}</p>
                  {alias_block}
                  <div class="document-card__actions">
                    <a class="button button--primary" href="{root_prefix}{document["url"]}" target="_blank" rel="noreferrer">Open PDF</a>
                    <button class="button button--secondary" type="button" data-view-document="{index}">View below</button>
                  </div>
                </article>
                """
            )
        )
    return "\n".join(cards)


def render_preview_cards(previews: list[dict], root_prefix: str, lightbox_group: str) -> str:
    cards: list[str] = []
    for preview in previews:
        cards.append(
            strip_margin(
                f"""
                <figure class="preview-card">
                  <a class="preview-card__link" href="{root_prefix}{preview["src"]}" data-lightbox="{html.escape(lightbox_group)}" data-caption="{html.escape(preview["caption"])}">
                    <img src="{root_prefix}{preview["src"]}" alt="{html.escape(preview["caption"])}">
                  </a>
                  <figcaption>{html.escape(preview["caption"])}</figcaption>
                </figure>
                """
            )
        )
    return "\n".join(cards)


def render_project_card(project: dict) -> str:
    tags = " ".join(tag.lower() for tag in project["tags"])
    return strip_margin(
        f"""
        <article class="project-card" data-tags="{html.escape(tags)}">
          <a class="project-card__thumb" href="projects/{project["slug"]}.html">
            <img src="{project["thumbnail"]}" alt="{html.escape(project["title"])} preview">
          </a>
          <div class="project-card__body">
            <div class="project-card__meta">
              <span>{html.escape(project["category"])}</span>
              <span>{html.escape(project["reference"])}</span>
            </div>
            <h2><a href="projects/{project["slug"]}.html">{html.escape(project["title"])}</a></h2>
            <p class="project-card__subtitle">{html.escape(project["subtitle"])}</p>
            <p>{html.escape(project["summary"])}</p>
            <ul class="tag-list">{render_tags(project["tags"])}</ul>
            <a class="text-link" href="projects/{project["slug"]}.html">View project</a>
          </div>
        </article>
        """
    )


def render_document_frame(documents: list[dict], root_prefix: str) -> str:
    payload = [
        {
            "label": document["label"],
            "summary": document["summary"],
            "url": f"{root_prefix}{document['url']}",
            "open_url": f"{root_prefix}{document['url']}",
            "file_name": document["file_name"],
            "page_count": document["page_count"],
        }
        for document in documents
    ]
    return strip_margin(
        f"""
        <div class="document-frame" data-documents="{html.escape(json.dumps(payload))}">
          <div class="document-frame__toolbar">
            <div class="document-frame__tabs" data-role="tabs"></div>
            <a class="button button--primary" data-role="open-link" href="{root_prefix}{documents[0]["url"]}" target="_blank" rel="noreferrer">Open active PDF</a>
          </div>
          <div class="document-frame__meta" data-role="meta"></div>
          <iframe class="document-frame__viewer" data-role="iframe" title="Project document viewer" loading="lazy"></iframe>
        </div>
        """
    )


def render_header(root_prefix: str) -> str:
    home_href = f"{root_prefix}index.html"
    documents_href = f"{root_prefix}documents.html"
    return strip_margin(
        f"""
        <header class="site-header shell">
          <a class="site-header__mark" href="{home_href}">Daniel Heard</a>
          <nav class="site-nav">
            <a href="{home_href}">Projects</a>
            <a href="{documents_href}">Document library</a>
          </nav>
        </header>
        """
    )


def render_head(title: str, description: str, root_prefix: str, include_project_script: bool = False, include_site_script: bool = False) -> str:
    script_tags = []
    if include_site_script:
        script_tags.append(f'  <script defer src="{root_prefix}assets/js/site.js"></script>')
    if include_project_script:
        script_tags.append(f'  <script defer src="{root_prefix}assets/js/project.js"></script>')
    scripts = "\n".join(script_tags)
    return strip_margin(
        f"""
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{html.escape(title)}</title>
          <meta name="description" content="{html.escape(description)}">
          <link rel="preconnect" href="https://fonts.googleapis.com">
          <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
          <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
          <link rel="stylesheet" href="{root_prefix}assets/css/styles.css">
        {scripts}
        </head>
        """
    )


def render_footer(root_prefix: str) -> str:
    return strip_margin(
        f"""
        <footer class="site-footer shell">
          <p>Daniel Heard - Engineering Project Portfolio</p>
          <p>Selected professional and academic engineering work prepared for employer review.</p>
          <p><a href="{root_prefix}documents.html">Open the full document library</a></p>
        </footer>
        """
    )


def build_project_record(project_spec: ProjectSpec) -> dict:
    documents: list[dict] = []
    materialized: dict[str, Path] = {}
    file_total = 0

    for document_spec in project_spec.documents:
        materialized_sources = [materialize_source(source, PDF_OUTPUT) for source in document_spec.sources]
        primary_path = materialized_sources[0]
        materialized[document_spec.key] = primary_path
        file_total += len(materialized_sources)
        documents.append(
            {
                "key": document_spec.key,
                "label": document_spec.label,
                "summary": document_spec.summary,
                "file_name": primary_path.name,
                "url": url_for(primary_path),
                "page_count": page_count(primary_path),
                "source_origin": document_spec.sources[0].origin_label,
                "aliases": [
                    {"name": alias_path.name, "url": url_for(alias_path)}
                    for alias_path in materialized_sources[1:]
                ],
            }
        )

    main_document_path = materialized[project_spec.main_document_key]
    thumbnail_path = THUMB_OUTPUT / f"{project_spec.slug}-thumb.jpg"
    thumbnail_image = build_card_thumbnail(render_pdf_page(main_document_path, 1, scale=1.7))
    save_image(thumbnail_image, thumbnail_path)

    previews: list[dict] = []
    for index, preview_spec in enumerate(project_spec.previews, start=1):
        preview_source = materialized[preview_spec.document_key]
        preview_path = PREVIEW_OUTPUT / f"{project_spec.slug}-preview-{index}.jpg"
        preview_image = fit_preview(render_pdf_page(preview_source, preview_spec.page, scale=2.0))
        save_image(preview_image, preview_path)
        previews.append({"src": url_for(preview_path), "caption": preview_spec.caption})

    return {
        "id": project_spec.id,
        "slug": project_spec.slug,
        "title": project_spec.title,
        "subtitle": project_spec.subtitle,
        "category": project_spec.category,
        "discipline": project_spec.discipline,
        "work_stream": project_spec.work_stream,
        "reference": project_spec.reference,
        "authorship": project_spec.authorship,
        "source_batch": project_spec.source_batch,
        "tags": list(project_spec.tags),
        "summary": project_spec.summary,
        "role": project_spec.role,
        "scope": list(project_spec.scope),
        "deliverables": list(project_spec.deliverables),
        "thumbnail": url_for(thumbnail_path),
        "previews": previews,
        "documents": documents,
        "file_total": file_total,
    }


def build_library_file_record(spec: LibraryFileSpec) -> dict:
    output_dir = FILE_OUTPUT
    materialized = materialize_source(spec.source, output_dir)
    return {
        "title": spec.title,
        "summary": spec.summary,
        "file_name": materialized.name,
        "url": url_for(materialized),
        "file_type": spec.file_type,
        "work_stream": spec.work_stream,
        "source_batch": spec.source_batch,
    }


def build_archive_record(spec: ArchiveSpec) -> dict:
    materialized = materialize_source(spec.source, FILE_OUTPUT)
    return {
        "title": spec.title,
        "summary": spec.summary,
        "file_name": materialized.name,
        "url": url_for(materialized),
        "file_type": materialized.suffix.lstrip("."),
    }


def write_index(projects: list[dict]) -> None:
    grouped = {section: [project for project in projects if project["work_stream"] == section] for section in PROJECT_SECTION_ORDER}
    professional_count = len(grouped["Professional Work"])
    academic_count = len(grouped["Academic Work"])
    unique_documents = sum(len(project["documents"]) for project in projects)
    supplied_files = sum(project["file_total"] for project in projects) + len(LIBRARY_FILES) + len(ARCHIVES)

    project_sections: list[str] = []
    for section in PROJECT_SECTION_ORDER:
        cards = "\n".join(render_project_card(project) for project in grouped[section])
        intro = (
            "Consultancy calculation packs, proposal sheets, and temporary works packages from live project work."
            if section == "Professional Work"
            else "Selected university coursework, group reports, and dissertation work included as supporting technical evidence."
        )
        project_sections.append(
            strip_margin(
                f"""
                <section class="section shell">
                  <div class="section__header">
                    <div>
                      <p class="eyebrow">{html.escape(section)}</p>
                      <h2>{html.escape(section)}</h2>
                    </div>
                    <p class="section__intro">{html.escape(intro)}</p>
                  </div>
                  <div class="project-grid">
                    {cards}
                  </div>
                </section>
                """
            )
        )

    index_html = strip_margin(
        f"""
        <!doctype html>
        <html lang="en">
        {render_head("Daniel Heard | Engineering Project Portfolio", "Selected professional and academic engineering work presented with direct access to the underlying documents.", "", include_site_script=True)}
        <body>
          <div class="page-rules" aria-hidden="true"></div>
          {render_header("")}
          <main>
            <section class="hero shell">
              <div class="hero__copy">
                <p class="eyebrow">Selected Structural and Civil Engineering Work</p>
                <h1>Engineering Project Portfolio</h1>
                <p class="hero__name">Daniel Heard</p>
                <p class="hero__summary">
                  A selection of structural and civil engineering work spanning consultancy calculation packs,
                  temporary works, structural alterations, and university design submissions. Professional and
                  academic work are separated clearly, with each project page giving brief context, selected
                  preview pages, and direct access to the underlying document set.
                </p>
              </div>
              <aside class="hero__panel">
                <div class="hero__panel-row">
                  <span>Professional projects</span>
                  <strong>{professional_count}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>Academic projects</span>
                  <strong>{academic_count}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>Document sets</span>
                  <strong>{unique_documents + len(LIBRARY_FILES)}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>Total files</span>
                  <strong>{supplied_files}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>In-browser viewing</span>
                  <strong>Native PDF viewer</strong>
                </div>
                <p class="hero__panel-note">
                  Preview pages can be opened full-screen, and every project page keeps clear Open PDF
                  actions alongside the in-browser viewer for quick review.
                </p>
              </aside>
            </section>

            <section class="section shell">
              <div class="section__header">
                <div>
                  <p class="eyebrow">Browse</p>
                  <h2>Filter projects</h2>
                </div>
                <p class="section__intro">
                  Filter by work type or topic. The professional work is front and centre, with academic
                  material retained separately as supporting evidence of technical range.
                </p>
              </div>
              <div class="filter-bar" aria-label="Project filters">
                <button class="filter-chip is-active" data-filter="all" type="button">All</button>
                <button class="filter-chip" data-filter="professional" type="button">Professional</button>
                <button class="filter-chip" data-filter="academic" type="button">Academic</button>
                <button class="filter-chip" data-filter="temporary works" type="button">Temporary Works</button>
                <button class="filter-chip" data-filter="foundations" type="button">Foundations</button>
                <button class="filter-chip" data-filter="alterations" type="button">Alterations</button>
                <button class="filter-chip" data-filter="timber" type="button">Timber</button>
                <button class="filter-chip" data-filter="geotechnical" type="button">Geotechnical</button>
                <button class="filter-chip" data-filter="research" type="button">Research</button>
              </div>
            </section>

            {"".join(project_sections)}

            <section class="section shell">
              <div class="section__header">
                <div>
                  <p class="eyebrow">Reference Library</p>
                  <h2>Complete document library</h2>
                </div>
                <p class="section__intro">
                  Every project PDF, supporting file, and supplied source bundle is available on a separate
                  reference page with original filenames preserved.
                </p>
              </div>
              <div class="library-callout">
                <p>
                  Use the document library to review every file included in the portfolio, grouped alongside
                  the related project pages.
                </p>
                <a class="button button--primary" href="documents.html">Open document library</a>
              </div>
            </section>
          </main>
          {render_footer("")}
        </body>
        </html>
        """
    )
    write_text(ROOT / "index.html", index_html)


def write_project_page(project: dict) -> None:
    root_prefix = "../"
    document_cards = render_document_cards(project["documents"], root_prefix)
    preview_cards = render_preview_cards(project["previews"], root_prefix, project["slug"])
    page_html = strip_margin(
        f"""
        <!doctype html>
        <html lang="en">
        {render_head(f'{project["title"]} | Daniel Heard', project["summary"], root_prefix, include_project_script=True)}
        <body>
          <div class="page-rules" aria-hidden="true"></div>
          {render_header(root_prefix)}
          <main>
            <section class="project-hero shell">
              <a class="back-link" href="../index.html">All projects</a>
              <div class="project-hero__grid">
                <div class="project-hero__copy">
                  <p class="eyebrow">{html.escape(project["category"])} - {html.escape(project["reference"])}</p>
                  <h1 class="project-page-title">{html.escape(project["title"])}</h1>
                  <p class="project-hero__subtitle">{html.escape(project["subtitle"])}</p>
                  <p class="project-hero__summary">{html.escape(project["summary"])}</p>
                </div>
                <aside class="meta-panel">
                  <h2>Project information</h2>
                  <dl>{render_meta_rows(project)}</dl>
                </aside>
              </div>
            </section>

            <section class="section shell">
              <div class="detail-grid">
                <article class="detail-card">
                  <h2>My role</h2>
                  <p>{html.escape(project["role"])}</p>
                </article>
                <article class="detail-card">
                  <h2>Scope / key checks</h2>
                  <ul>{render_list(project["scope"])}</ul>
                </article>
                <article class="detail-card">
                  <h2>Deliverables</h2>
                  <ul>{render_list(project["deliverables"])}</ul>
                </article>
              </div>
            </section>

            <section class="section shell">
              <div class="section__header">
                <div>
                  <p class="eyebrow">Preview pages</p>
                  <h2>Click to inspect full-screen</h2>
                </div>
                <p class="section__intro">
                  Selected pages from the document set to give a quick view of the calculation or report format.
                  Click any image to open a full-screen view.
                </p>
              </div>
              <div class="preview-grid">
                {preview_cards}
              </div>
            </section>

            <section class="section shell">
              <div class="section__header">
                <div>
                  <p class="eyebrow">Project documents</p>
                  <h2>Document set</h2>
                </div>
                <p class="section__intro">
                  The files below form the project document set. They can be opened directly or viewed in-browser
                  using the embedded PDF frame.
                </p>
              </div>
              <div class="document-grid">
                {document_cards}
              </div>
            </section>

            <section class="section shell">
              <div class="section__header viewer-header">
                <div>
                  <p class="eyebrow">In-browser viewing</p>
                  <h2>Project viewer</h2>
                </div>
                <p class="section__intro">
                  Use the tabs below to switch documents. The active PDF can always be opened in a new tab with
                  the button beside the viewer.
                </p>
              </div>
              {render_document_frame(project["documents"], root_prefix)}
            </section>
          </main>
          {render_footer(root_prefix)}
        </body>
        </html>
        """
    )
    write_text(PROJECT_OUTPUT / f"{project['slug']}.html", page_html)


def render_library_group(title: str, intro: str, items: list[str]) -> str:
    return strip_margin(
        f"""
        <section class="section shell">
          <div class="section__header">
            <div>
              <p class="eyebrow">Document library</p>
              <h2>{html.escape(title)}</h2>
            </div>
            <p class="section__intro">{html.escape(intro)}</p>
          </div>
          <div class="library-grid">
            {"".join(items)}
          </div>
        </section>
        """
    )


def render_library_card(title: str, summary: str, file_name: str, file_url: str, button_label: str, source_batch: str, extra_links: str = "", project_link: str = "") -> str:
    project_html = ""
    if project_link:
        project_html = f'<a class="text-link" href="{project_link}">Open related project page</a>'
    return strip_margin(
        f"""
        <article class="library-card">
          <div class="library-card__meta">
            <span>{html.escape(source_batch)}</span>
            <span>{html.escape(file_name)}</span>
          </div>
          <h3>{html.escape(title)}</h3>
          <p>{html.escape(summary)}</p>
          {extra_links}
          <div class="document-card__actions">
            <a class="button button--primary" href="{file_url}" target="_blank" rel="noreferrer">{html.escape(button_label)}</a>
            {project_html}
          </div>
        </article>
        """
    )


def write_documents_page(projects: list[dict], extra_files: list[dict], archives: list[dict]) -> None:
    project_cards: list[str] = []
    for project in projects:
        for document in project["documents"]:
            alias_html = ""
            if document["aliases"]:
                alias_links = ", ".join(
                    f'<a href="{alias["url"]}" target="_blank" rel="noreferrer">{html.escape(alias["name"])}</a>'
                    for alias in document["aliases"]
                )
                alias_html = f'<p class="library-card__aliases">Additional filenames: {alias_links}</p>'
            project_cards.append(
                render_library_card(
                    title=document["label"],
                    summary=document["summary"],
                    file_name=document["file_name"],
                    file_url=document["url"],
                    button_label="Open PDF",
                    source_batch=f'{project["category"]} - {project["reference"]}',
                    extra_links=alias_html,
                    project_link=f'projects/{project["slug"]}.html',
                )
            )

    extra_cards = [
        render_library_card(
            title=file_record["title"],
            summary=file_record["summary"],
            file_name=file_record["file_name"],
            file_url=file_record["url"],
            button_label="Download file",
            source_batch="Supporting file",
        )
        for file_record in extra_files
    ]

    archive_cards = [
        render_library_card(
            title=archive["title"],
            summary=archive["summary"],
            file_name=archive["file_name"],
            file_url=archive["url"],
            button_label="Download bundle",
            source_batch="Source bundle",
        )
        for archive in archives
    ]

    page_html = strip_margin(
        f"""
        <!doctype html>
        <html lang="en">
        {render_head("Document Library | Daniel Heard", "Complete reference library for the portfolio, including project PDFs, supporting files, and source bundles.", "")}
        <body>
          <div class="page-rules" aria-hidden="true"></div>
          {render_header("")}
          <main>
            <section class="hero shell hero--compact">
              <div class="hero__copy">
                <p class="eyebrow">Reference Library</p>
                <h1 class="hero__title-small">Document Library</h1>
                <p class="hero__summary">
                  Every file included in the portfolio is listed here with its original filename preserved.
                  Project documents link back to their individual project pages, while supporting files and
                  supplied source bundles remain available separately.
                </p>
              </div>
              <aside class="hero__panel">
                <div class="hero__panel-row">
                  <span>Project PDFs</span>
                  <strong>{sum(len(project["documents"]) for project in projects)}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>Supplementary files</span>
                  <strong>{len(extra_files)}</strong>
                </div>
                <div class="hero__panel-row">
                  <span>Source bundles</span>
                  <strong>{len(archives)}</strong>
                </div>
              </aside>
            </section>
            {render_library_group("Project PDFs", "Project documents grouped on the portfolio pages and listed here with original filenames preserved.", project_cards)}
            {render_library_group("Supporting files", "Non-PDF files included alongside the portfolio documents.", extra_cards)}
            {render_library_group("Source bundles", "Original zip bundles retained in the repository for completeness.", archive_cards)}
          </main>
          {render_footer("")}
        </body>
        </html>
        """
    )
    write_text(ROOT / "documents.html", page_html)


def write_data_file(projects: list[dict], extra_files: list[dict], archives: list[dict]) -> None:
    payload = {
        "source_scope": {
            "downloads_date": "2026-04-18",
            "notes": "Portfolio rebuilt from the supplied April 18, 2026 C8676 temporary-works PDFs together with the supplied professional and academic source bundles. Older files such as C9211 were intentionally excluded after clarification.",
        },
        "projects": projects,
        "supplementary_files": extra_files,
        "archives": archives,
    }
    write_text(DATA_OUTPUT / "projects.json", json.dumps(payload, indent=2))


def write_docs(projects: list[dict], extra_files: list[dict], archives: list[dict]) -> None:
    manifest = {
        "mode": "original-source-files",
        "redaction_applied": False,
        "notes": [
            "No redaction was applied. The user explicitly requested that the original files remain unchanged.",
            "Professional work is limited to the supplied C8676 temporary-works PDFs together with the consultancy packs held in the supplied professional source bundles.",
            "Academic work covers the supplied coursework, group reports, and dissertation material.",
            "Older files such as C9211 were excluded after user clarification.",
        ],
        "files": [
            {
                "title": document["file_name"],
                "url": document["url"],
                "source": document["source_origin"],
                "redaction_applied": False,
            }
            for project in projects
            for document in project["documents"]
        ]
        + [
            {
                "title": file_record["file_name"],
                "url": file_record["url"],
                "source": file_record["source_batch"],
                "redaction_applied": False,
            }
            for file_record in extra_files
        ]
        + [
            {
                "title": archive["file_name"],
                "url": archive["url"],
                "source": "Downloads",
                "redaction_applied": False,
            }
            for archive in archives
        ],
    }
    write_text(DOCS_OUTPUT / "redaction-manifest.json", json.dumps(manifest, indent=2))

    redaction_review = strip_margin(
        """
        # Redaction Review

        No redaction was applied.

        The current portfolio uses the original source files exactly as supplied, following the user's
        explicit instruction to keep the documents unchanged and to stop blocking Case Consultants details.

        Scope note:
        - Professional work is limited to the supplied C8676 temporary-works PDFs together with the consultancy packs held in the supplied professional source bundles.
        - Older files such as C9211 were intentionally excluded after clarification.
        - Academic work covers the supplied coursework, group reports, and dissertation material.
        """
    )
    write_text(DOCS_OUTPUT / "redaction-review.md", redaction_review)

    qa_report = strip_margin(
        f"""
        # QA Report

        Date: 2026-04-18

        Checks completed:
        - Rebuilt the site from the corrected source set only.
        - Excluded C9211 and other older professional PDFs.
        - Copied original PDFs, the spreadsheet file, and all supplied source bundles unchanged into the repo.
        - Replaced slow PDF.js page rendering with a single native PDF iframe per project page.
        - Added click-to-full-screen preview images on project pages.
        - Generated a full document library page covering every supplied source file and bundle.

        Totals:
        - Project pages: {len(projects)}
        - Distinct project documents: {sum(len(project["documents"]) for project in projects)}
        - Supplementary files: {len(extra_files)}
        - Source bundles: {len(archives)}
        """
    )
    write_text(DOCS_OUTPUT / "qa-report.md", qa_report)

    known_issues = strip_margin(
        """
        # Known Issues

        - Native PDF viewing performance depends on the browser's built-in PDF engine and the size of the source file.
          This is still materially faster than rendering every page through PDF.js, and every page includes a prominent Open PDF button as fallback.
        - The supplementary spreadsheet file is included in the document library but is not rendered in-browser.
        """
    )
    write_text(DOCS_OUTPUT / "known-issues.md", known_issues)


def clean_output() -> None:
    targets = [
        PDF_OUTPUT.parent,
        FILE_OUTPUT.parent,
        ROOT / "images",
        PROJECT_OUTPUT,
        DATA_OUTPUT,
        DOCS_OUTPUT,
    ]
    for target in targets:
        if target.exists():
            shutil.rmtree(target)

    for root_file in (ROOT / "index.html", ROOT / "documents.html"):
        if root_file.exists():
            root_file.unlink()

    DOCS_OUTPUT.mkdir(parents=True, exist_ok=True)


def build() -> None:
    clean_output()

    projects = [build_project_record(project_spec) for project_spec in PROJECTS]
    extra_files = [build_library_file_record(spec) for spec in LIBRARY_FILES]
    archives = [build_archive_record(spec) for spec in ARCHIVES]

    write_index(projects)
    for project in projects:
        write_project_page(project)
    write_documents_page(projects, extra_files, archives)
    write_data_file(projects, extra_files, archives)
    write_docs(projects, extra_files, archives)


if __name__ == "__main__":
    build()
