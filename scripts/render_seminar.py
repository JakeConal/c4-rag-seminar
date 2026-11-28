"""Render the seminar report and slides from the Markdown and measured logs."""

import argparse
import re
from pathlib import Path
from xml.sax.saxutils import escape

from markdown_it import MarkdownIt
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle

from ragstudy.common import metrics, read_json, write_json

ROOT = Path(__file__).resolve().parents[1]
PAPER = HexColor('#F7F5EF')
INK = HexColor('#172723')
PINE = HexColor('#10352D')
GREEN = HexColor('#23634F')
MUTED = HexColor('#53625A')
LINE = HexColor('#D4DED5')
MINT = HexColor('#DBEDE3')
BASE = HexColor('#596E65')
TEAL = HexColor('#20785D')
RUST = HexColor('#AD452B')
ROSE = HexColor('#F3DFD5')
GOLD = HexColor('#F1A773')
WIDTH, HEIGHT = 960, 540
LEFT, RIGHT = 56, WIDTH - 56
TEAM = '23120045  /  23120124  /  23120175'
QUALITY = {'mrr_at_5': 'MRR@5', 'recall_at_5': 'Recall@5'}
LATENCY = {'p50_ms': 'p50', 'p95_ms': 'p95'}


def render_report():
    parser = MarkdownIt().enable('table')
    # Bundle the licensed font so Vietnamese author names render on any host.
    pdfmetrics.registerFont(TTFont('ReportAuthors', str(ROOT / 'assets/fonts/DejaVuSans.ttf')))
    body = ParagraphStyle('Body', fontName='Times-Roman', fontSize=10.5, leading=12.6,
                          textColor=black, spaceAfter=5)
    title = ParagraphStyle('Title', parent=body, fontName='Times-Bold', fontSize=22,
                           leading=25, spaceBefore=7, spaceAfter=6)
    heading = ParagraphStyle('Heading', parent=body, fontName='Times-Bold',
                             fontSize=12, leading=15, spaceBefore=9, spaceAfter=6,
                             keepWithNext=True)
    cell = ParagraphStyle('Cell', parent=body, fontSize=9.1, leading=12)
    cell_header = ParagraphStyle('Cell header', parent=cell, textColor=black,
                                 fontName='Times-Bold')
    subheading = ParagraphStyle('Subheading', parent=heading, fontSize=11, leading=13)
    authors = ParagraphStyle('Authors', parent=body, fontName='ReportAuthors', fontSize=8.5, leading=12, alignment=1)
    caption = ParagraphStyle('Caption', parent=body, fontName='Times-Roman', fontSize=9, leading=11, alignment=1, keepWithNext=True)
    references = ParagraphStyle('References', parent=body, fontSize=9, leading=10.8, leftIndent=15, firstLineIndent=-15)
    source = (ROOT / 'REPORT.md').read_text()
    flow = []
    for chunk in source.split('<!-- pagebreak -->'):
        if flow:
            flow.append(PageBreak())
        tokens = parser.parse(chunk.strip())
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token.type == 'table_open':
                rows = []
                while tokens[index].type != 'table_close':
                    current = tokens[index]
                    if current.type == 'tr_open':
                        rows.append([])
                    if current.type in ('th_open', 'td_open'):
                        style = cell_header if current.type == 'th_open' else cell
                        rows[-1].append(Paragraph(inline_html(parser, tokens[index + 1].content),
                                                  style))
                    index += 1
                widths = [100, 121, 121, 151] if len(rows[0]) == 4 else None
                table = Table(rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
                table.setStyle(TableStyle([
                    ('LINEABOVE', (0, 0), (-1, 0), .8, black),
                    ('LINEBELOW', (0, 0), (-1, 0), .5, black),
                    ('LINEBELOW', (0, -1), (-1, -1), .8, black),
                    ('TOPPADDING', (0, 0), (-1, -1), 5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                table.spaceAfter = 11
                flow.append(table)
            if token.type in ('heading_open', 'paragraph_open'):
                content = tokens[index + 1].content
                style = {'h1': title, 'h2': heading, 'h3': subheading, 'p': body}[token.tag]
                if content.startswith('Dương '):
                    style = authors
                elif content.startswith('**TABLE '):
                    style = caption
                elif re.match(r'^\[[1-4]\] ', content):
                    style = references
                flow.append(Paragraph(inline_html(parser, content), style))
            index += 1
    document = SimpleDocTemplate(str(ROOT / 'report.pdf'), pagesize=A4, title='C4 | Chunking and reranking for RAG',
                                 author=TEAM, leftMargin=45, rightMargin=45, topMargin=44,
                                 bottomMargin=40, invariant=1)

    def footer(canvas, doc):
        canvas.setFillColor(TEAL)
        canvas.rect(45, A4[1] - 25, 28, 3, stroke=0, fill=1)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(A4[0] - 45, A4[1] - 25, 'C4  /  EMPIRICAL RETRIEVAL STUDY')
        canvas.setStrokeColor(LINE)
        canvas.line(45, 29, A4[0] - 45, 29)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(45, 17, 'C4   /   CSC13114 CQ2023/3')
        canvas.drawRightString(A4[0] - 45, 17, str(doc.page))

    document.build(flow, onFirstPage=footer, onLaterPages=footer)
    if document.page > 3:
        raise ValueError(f'Report exceeds three pages ({document.page})')


def inline_html(parser, source):
    source = re.sub(r'^(https://github\.com/[^\s]+)$', r'<\1>', source)
    markup = parser.renderInline(source).strip()
    markup = re.sub(r'href="(?!https?://|#)([^"]+)"',
                    r'href="https://github.com/JakeConal/c4-rag-seminar/blob/main/\1"', markup)
    replacements = {'<strong>': '<b>', '</strong>': '</b>', '<em>': '<i>', '</em>': '</i>',
                    '<code>': '<font face="Courier" size="9">', '</code>': '</font>',
                    '<a ': '<a color="#23634F" '}
    for old, new in replacements.items():
        markup = markup.replace(old, new)
    return markup


def pct(value):
    return f'{100 * value:.2f}%'


def points(value):
    return f'{100 * value:+.2f} pp'


def first_hit(ranked, relevant):
    return next((i for i, doc in enumerate(ranked, 1) if doc in relevant), None)


def diagnostics(result_path):
    rows = read_json(result_path / 'run-01.json')['queries']
    mapping = read_json(result_path / 'chunk-map.json')
    findings = []
    for row in rows:
        relevant = set(row['relevant'])
        candidates = [mapping[chunk] for chunk in row['baseline']['candidates']]
        candidate_rank = first_hit(list(dict.fromkeys(candidates)), relevant)
        baseline = metrics(row['baseline']['docs'], relevant)['mrr_at_5']
        reranked = metrics(row['reranked']['docs'], relevant)['mrr_at_5']
        findings.append((row, candidate_rank, baseline, reranked))
    wins = [case for case in findings if case[3] > case[2]]
    losses = [case for case in findings if case[3] < case[2]]
    misses = [case for case in findings if case[1] is None]
    wins.sort(key=lambda case: (-(case[3] - case[2]), len(case[0]['query'])))
    losses.sort(key=lambda case: (case[3] - case[2], len(case[0]['query'])))
    misses.sort(key=lambda case: len(case[0]['query']))
    return rows, wins, losses, misses


def export_display_values(result_path, environment, summary, chunking, stats):
    aggregate = summary['across_runs']

    def displayed_spread(group, keys, formatter):
        return {
            key: {stat: formatter(aggregate[group][key][stat]) for stat in ('median', 'min', 'max')}
            for key in keys
        }

    def milliseconds(value):
        return f'{value:.1f}'

    def added_milliseconds(value):
        return f'{value:+.1f}'

    def mib(value):
        return f'{value / 2**20:.2f}'

    rows, wins, losses, misses = stats
    query_examples = {}
    for name, selection in [('promoted', wins), ('demoted', losses), ('pool_miss', misses)]:
        if selection:
            row, parent_rank, _, _ = selection[0]
            relevant = set(row['relevant'])
            query_examples[name] = {
                'query_id': row['query_id'],
                'judged_relevant_documents': sorted(relevant),
                'vector_pool_first_relevant_parent_rank': parent_rank,
                'baseline_top5_first_relevant_rank': first_hit(row['baseline']['docs'], relevant),
                'reranked_top5_first_relevant_rank': first_hit(row['reranked']['docs'], relevant),
                'baseline_ms': milliseconds(row['baseline']['latency_ms']),
                'reranked_ms': milliseconds(row['reranked']['latency_ms']),
            }
    first_pass = summary['runs'][0]
    chunk_display = {}
    for arm in ('baseline', 'alternative'):
        values = chunking[arm]
        chunk_display[arm] = {
            'window_tokens': values['window_tokens'],
            'stride_tokens': values['window_tokens'] - chunking['overlap_tokens'],
            'chunks': values['chunks'],
            'embedding_matrix_mib': mib(values['index_bytes']),
            'pool_recall': pct(values['pool_recall']),
            'mrr_at_5': pct(values['mrr_at_5']),
            'recall_at_5': pct(values['recall_at_5']),
        }
    a, b = chunking['baseline'], chunking['alternative']
    chunk_display['change'] = {
        'chunks': b['chunks'] - a['chunks'],
        'embedding_matrix_mib': f"{(b['index_bytes'] - a['index_bytes']) / 2**20:+.2f}",
        **{key: points(b[key] - a[key]) for key in ('pool_recall', 'mrr_at_5', 'recall_at_5')},
    }
    write_json(result_path / 'presentation-values.json', {
        'note': 'Display rounding only. Source files are relative to this result directory.',
        'sources': {
            'setup': 'environment.json',
            'pass_statistics': 'summary.json',
            'raw_runs': [f'run-{run:02d}.json' for run in range(1, summary['run_count'] + 1)],
            'chunk_to_parent_mapping': 'chunk-map.json',
            'chunk_comparison': 'chunk-ablation/summary.json',
        },
        'study': {
            'documents': environment['data']['documents'],
            'chunks': environment['data']['chunks'],
            'claims_per_pass': len(rows),
            'passes': summary['run_count'],
            'paired_query_observations': len(rows) * summary['run_count'],
            'embedding_matrix_mib': mib(environment['index_bytes']),
            'index_build_seconds': f"{environment['index_build_ms'] / 1_000:.1f}",
        },
        'quality': {
            'baseline': displayed_spread('baseline', QUALITY, pct),
            'reranked': displayed_spread('reranked', QUALITY, pct),
            'percentage_point_change': displayed_spread('quality_delta', QUALITY, points),
        },
        'latency_ms': {
            'baseline': displayed_spread('baseline', LATENCY, milliseconds),
            'reranked': displayed_spread('reranked', LATENCY, milliseconds),
            'paired_added': displayed_spread('added_latency', LATENCY, added_milliseconds),
        },
        'first_pass': {
            'mrr_at_5_query_counts': first_pass['mrr_at_5_query_counts'],
            'recall_at_5_query_counts': first_pass['recall_at_5_query_counts'],
            'claims_without_judged_candidate': len(misses),
            'mean_distinct_parents': f"{first_pass['candidate_pool']['mean_distinct_parents']:.1f}",
            'candidate_oracle_recall_at_5': pct(first_pass['candidate_pool']['oracle_recall_at_5']),
            'query_examples': query_examples,
        },
        'chunk_comparison': chunk_display,
    })


class Slides:
    def __init__(self):
        self.canvas = Canvas(str(ROOT / 'slides.pdf'), pagesize=(WIDTH, HEIGHT), pageCompression=1,
                             invariant=1)
        self.canvas.setTitle('C4 | Chunking and reranking for RAG')
        self.canvas.setAuthor(TEAM)
        self.number = 0

    def box(self, x, y, w, h, color, radius=0):
        self.canvas.setFillColor(color)
        self.canvas.roundRect(x, HEIGHT - y - h, w, h, radius, stroke=0, fill=1)

    def line(self, x, y, end_x, end_y, color=LINE, weight=1):
        self.canvas.setStrokeColor(color)
        self.canvas.setLineWidth(weight)
        self.canvas.line(x, HEIGHT - y, end_x, HEIGHT - end_y)

    def label(self, value, x, y, size=13, font='Helvetica-Bold', color=MUTED, align='left'):
        self.canvas.setFont(font, size)
        self.canvas.setFillColor(color)
        method = self.canvas.drawRightString if align == 'right' else self.canvas.drawString
        method(x, HEIGHT - y - size, str(value))

    def paragraph(self, value, x, y, w, size=18, color=INK, leading=None, max_height=None):
        style = ParagraphStyle('Slide paragraph', fontName='Helvetica', fontSize=size,
                               leading=leading or size * 1.28, textColor=color)
        paragraph = Paragraph(escape(value), style)
        _, height = paragraph.wrap(w, HEIGHT)
        if max_height is not None and height > max_height:
            raise ValueError(f'Slide {self.number} text exceeds its area: {value}')
        paragraph.drawOn(self.canvas, x, HEIGHT - y - height)
        return height

    def arrow(self, x, y, end_x):
        self.line(x, y, end_x, y, color=TEAL, weight=2)
        self.line(end_x - 7, y - 4, end_x, y, color=TEAL, weight=2)
        self.line(end_x - 7, y + 4, end_x, y, color=TEAL, weight=2)

    def start(self, section, headline, subtitle, evidence=None):
        self.number += 1
        self.box(0, 0, WIDTH, HEIGHT, PAPER)
        self.label(section.upper(), LEFT, 38, 12, color=TEAL)
        self.label(headline, LEFT, 63, 38, 'Times-Bold', INK)
        self.paragraph(subtitle, LEFT, 121, 808, 17, MUTED, max_height=45)
        self.line(LEFT, 493, RIGHT, 493)
        self.label(evidence or 'CSC13114 CQ2023/3   /   C4 seminar', LEFT, 506, 10,
                   'Helvetica', MUTED)
        self.label(f'{self.number:02d}', RIGHT, 503, 12, align='right')

    def next(self):
        self.canvas.showPage()

    def cover(self, aggregate):
        self.number += 1
        self.box(0, 0, WIDTH, HEIGHT, PINE)
        self.box(LEFT, 53, 56, 5, GOLD)
        self.label('CSC13114 CQ2023/3   /   C4 SEMINAR', LEFT, 78, 13, color=MINT)
        self.label('Chunking and', LEFT, 114, 64, 'Times-Bold', PAPER)
        self.label('reranking for RAG', LEFT, 178, 64, 'Times-Bold', PAPER)
        self.paragraph('Does reranking the vector top 50 improve the five documents we keep, '
                       'and how much latency does it add?', LEFT, 276, 672, 23, MINT)
        summary = [(points(aggregate['quality_delta']['mrr_at_5']['median']), 'MRR@5 change'),
                   (points(aggregate['quality_delta']['recall_at_5']['median']), 'Recall@5 change'),
                   (f"{aggregate['added_latency']['p95_ms']['median']:+.1f} ms",
                    'Paired added p95')]
        for index, (value, label) in enumerate(summary):
            x = LEFT + index * 283
            self.line(x, 374, x + 254, 374, GREEN, 1)
            self.label(value, x, 383, 32, color=GOLD)
            self.label(label, x, 424, 15, 'Helvetica', MINT)
        self.label(TEAM, LEFT, 502, 12, color=MINT)
        self.label('01', RIGHT, 502, 12, color=MINT, align='right')
        self.next()

    def workflow(self):
        self.start('Retrieval-augmented generation', 'Where retrieval fits in RAG',
                   'RAG gives a generator evidence from an external corpus. We measure the ranked output of retrieval.',
                   'Lewis et al. (2020)  /  Sentence Transformers retrieve-and-rerank guide')
        self.label('BEFORE REQUESTS', LEFT, 174, 13, color=TEAL)
        self.label('AT QUERY TIME', LEFT, 303, 13, color=TEAL)
        lanes = [
            (198, [('Source corpus', 'Titles and abstracts', white),
                   ('Split and embed', 'Token windows', white),
                   ('Store vectors', 'Vectors with parent IDs', MINT)]),
            (327, [('Query', 'Encode the claim', MINT),
                   ('Retrieve and rank', 'Return five parent IDs', PINE),
                   ('Assemble context', 'Select evidence text', white),
                   ('Generate answer', 'Condition on context', white)]),
        ]
        for y, stages in lanes:
            for i, (title, body, background) in enumerate(stages):
                x = LEFT + i * 217
                self.box(x, y, 197, 63, background, 7)
                self.label(title, x + 12, y + 8, 17, color=white if background == PINE else PINE)
                self.label(body, x + 12, y + 34, 14, 'Helvetica',
                           MINT if background == PINE else MUTED)
                if i < len(stages) - 1:
                    self.arrow(x + 199, y + 31, x + 214)
        self.line(368, 288, 588, 288, TEAL, 1.5)
        self.line(368, 288, 368, 322, TEAL, 1.5)
        self.line(588, 262, 588, 288, TEAL, 1.5)
        self.line(364, 317, 368, 322, TEAL, 1.5)
        self.line(372, 317, 368, 322, TEAL, 1.5)
        self.line(LEFT, 404, 470, 404, TEAL, 2)
        self.line(LEFT, 396, LEFT, 404, TEAL, 2)
        self.line(470, 396, 470, 404, TEAL, 2)
        self.label('Timed retrieval', LEFT, 415, 17, color=PINE)
        self.label('Quality from ranked IDs and SciFact judgments', LEFT, 442, 14,
                   'Helvetica', MUTED)
        self.label('Downstream RAG stages', 490, 415, 17, color=PINE)
        self.label('Context assembly and answer generation', 490, 442, 14,
                   'Helvetica', MUTED)
        self.next()

    def pipeline(self):
        self.start('Bi-encoder and cross-encoder', 'One candidate pool, two rankings',
                   'Both arms retrieve the same 50 chunks. Only the ordering step changes.',
                   'Sentence Transformers retrieve-and-rerank guide  /  config.json')
        self.box(LEFT, 183, 244, 168, PINE, 10)
        self.label('BI-ENCODER', LEFT + 19, 202, 11, color=MINT)
        self.label('Vector top 50', LEFT + 19, 222, 25, color=white)
        self.paragraph('Embed the query and each chunk independently. Compare their vectors by cosine similarity.',
                       LEFT + 19, 267, 209, 16, MINT, max_height=83)
        for y, bg, label, description in [
            (166, MINT, 'Baseline', 'Keep the cosine-similarity order.'),
            (274, ROSE, 'Cross-encoder', 'Read each query–chunk pair jointly, then sort by its relevance score.'),
        ]:
            self.arrow(300, y + 45, 325)
            self.box(332, y, 297, 88, bg, 9)
            self.label(label, 350, y + 12, 21, color=INK)
            self.paragraph(description, 350, y + 43, 265, 15, MUTED, max_height=40)
            self.arrow(635, y + 45, 660)
            self.box(667, y, 237, 88, white, 9)
            self.label('5 distinct documents', 680, y + 18, 19, color=INK)
            self.label('First chunk per parent wins.', 680, y + 49, 15, 'Helvetica', MUTED)
        self.box(LEFT, 391, RIGHT - LEFT, 75, white, 8)
        self.label('ILLUSTRATIVE PARENT DEDUPLICATION', LEFT + 16, 402, 12, color=TEAL)
        self.label('Ranked chunks   A1   A2   B1   C1', LEFT + 16, 426, 17, color=PINE)
        self.arrow(378, 437, 413)
        self.label('Unique parents   A   B   C', 436, 426, 17, color=PINE)
        self.label('A1 and A2 share parent A.', 700, 429, 14, 'Helvetica', MUTED)
        self.next()

    def chunking(self):
        self.start('Index construction', 'Chunk boundaries affect what ranks',
                   'The main comparison fixes the window at 192 embedding-tokenizer tokens, with 32 tokens of overlap.',
                   'Pinned MiniLM model card  /  Qu et al. (2025)  /  config.json')
        x = 167
        unit = 2.05
        for offset, y, color in ((0, 206, MINT), (160, 266, ROSE)):
            self.box(x + offset * unit, y, 192 * unit, 35, color, 6)
        self.box(x + 160 * unit, 206, 32 * unit, 95, HexColor('#DBB494'), 0)
        self.label('Window 1', LEFT, 214, 16, color=INK)
        self.label('Window 2', LEFT, 274, 16, color=INK)
        self.label('1', x, 185, 13)
        self.label('161', x + 160 * unit, 311, 13)
        self.label('192', x + 192 * unit, 185, 13, align='right')
        self.label('352', x + 352 * unit, 311, 13, align='right')
        self.label('32', x + 160 * unit + 22, 239, 20, color=PINE)
        self.label('160-token stride', 167, 311, 13, color=TEAL)
        for i, (heading, body) in enumerate([
            ('Fixed token windows', 'Smaller windows can focus the match. Larger windows can keep more context.'),
            ('Structure-aware splits', 'Use sentence or paragraph boundaries to preserve units of text.'),
            ('Semantic splits', 'Group related text and break where the topic changes.'),
        ]):
            start = LEFT + i * 288
            self.line(start, 354, start + 257, 354)
            self.label(heading, start, 365, 19, color=PINE)
            self.paragraph(body, start, 395, 250, 16, MUTED, max_height=70)
        self.next()

    def protocol(self, environment, summary):
        data = environment['data']
        config = environment['config']
        self.start('Controlled benchmark', 'Five paired passes on SciFact',
                   'Both arms use the same corpus, queries, candidate pool, hardware and load.',
                   'environment.json  /  chunk-map.json  /  run-01.json through run-05.json')
        measurements = [(f"{data['documents']:,}", 'abstracts'),
                        (f"{data['chunks']:,}", 'indexed chunks'),
                        (f"{environment['query_count']:,}", 'test claims per pass')]
        for i, (value, label) in enumerate(measurements):
            x = LEFT + i * 288
            self.box(x, 174, 271, 96, MINT, 9)
            self.label(value, x + 17, 183, 34, color=PINE)
            self.label(label, x + 18, 230, 17, 'Helvetica', PINE)
        cpu = environment['cpu'].split(' @')[0] or 'CPU host'
        controls = [
            ('Machine and load', f'{cpu}. {config["threads"]} PyTorch threads. Sequential queries. Batch size {config["batch_size"]}.'),
            ('Five full passes', f'{summary["run_count"] * environment["query_count"]:,} query pairs. Seeds 42–46 shuffle the claims. Arm order alternates after three warmup queries per arm.'),
            ('Timing boundary', 'Query encoding → search → optional reranking → five IDs. Index build and model loading happen before timing.'),
            ('One change', 'Both arms share exact cosine search, 192-token windows, 32-token overlap and the vector top-50 pool.'),
        ]
        for i, (heading, body) in enumerate(controls):
            x = LEFT + (i % 2) * 442
            y = 294 + (i // 2) * 94
            self.label(heading, x, y, 18, color=PINE)
            self.paragraph(body, x, y + 27, 403, 15, MUTED, max_height=63)
        self.next()

    def metrics_example(self):
        self.start('Worked example', 'Score one query at depth five',
                   'Toy example with two judged relevant parents, A and B. Green tiles mark hits.',
                   'Illustration only  /  study definitions and averaging in REPORT.md')
        self.label('RANK', 235, 166, 12, color=TEAL)
        for i in range(5):
            self.label(i + 1, 326 + i * 59, 166, 13, align='right')
        self.label('RECIPROCAL RANK', 607, 166, 12, color=TEAL)
        self.label('RECALL', 786, 166, 12, color=TEAL)
        for row, (arm, parents, rr, recall) in enumerate([
            ('Vector order', 'CADEF', '1 / 2 = 0.50', '1 / 2 = 0.50'),
            ('Reranked', 'ACBDE', '1 / 1 = 1.00', '2 / 2 = 1.00'),
        ]):
            y = 192 + row * 75
            self.box(LEFT, y, RIGHT - LEFT, 62, white, 8)
            self.label(arm, LEFT + 17, y + 18, 20, color=PINE)
            for i, parent in enumerate(parents):
                x = 294 + i * 59
                hit = parent in 'AB'
                self.box(x, y + 11, 47, 40, TEAL if hit else PAPER, 6)
                self.label(parent, x + 30, y + 16, 21,
                           color=white if hit else MUTED, align='right')
            self.label(rr, 607, y + 19, 18, color=PINE)
            self.label(recall, 786, y + 19, 18, color=PINE)
        self.line(LEFT, 365, RIGHT, 365)
        notes = [
            ('MRR@5', 'Average reciprocal rank across queries. A query scores zero when the first five have no hit.'),
            ('Recall@5', 'Average the share of each query’s judged relevant parents retrieved in the top five.'),
        ]
        for i, (heading, body) in enumerate(notes):
            x = LEFT + i * 435
            self.label(heading, x, 378, 19, color=PINE)
            self.paragraph(body, x, 405, 390, 16, MUTED, max_height=64)
        self.next()

    def quality(self, summary, result_path):
        aggregate = summary['across_runs']
        self.start('Measured retrieval quality', 'How do the top-five ranks change?',
                   f"Bars show the median of {summary['run_count']} pass means. Point changes use unrounded scores.",
                   f'{result_path.name}/summary.json  /  run-01.json for per-claim changes')
        chart_x, chart_w = 166, 410
        for tick in range(5):
            x = chart_x + chart_w * tick / 4
            self.line(x, 187, x, 414, LINE)
            self.label(f'{25 * tick}%', x - 10, 422, 12, 'Helvetica', MUTED)
        for i, (key, label) in enumerate(QUALITY.items()):
            y = 210 + 103 * i
            self.label(label, LEFT, y + 6, 21, color=PINE)
            delta = aggregate['quality_delta'][key]
            self.label(points(delta['median']), LEFT, y + 37, 16, color=TEAL)
            for j, (arm, fill) in enumerate((('baseline', BASE), ('reranked', TEAL))):
                value = aggregate[arm][key]['median']
                self.box(chart_x, y + j * 29, chart_w * value, 20, fill, 3)
                self.label(pct(value), chart_x + chart_w * value + 10, y + j * 29 + 1,
                           15, color=INK)
        self.box(620, 187, 284, 254, white, 8)
        self.label('CLAIM-LEVEL CHANGES', 636, 199, 13, color=TEAL)
        self.label('First full pass', 636, 225, 17, color=PINE)
        columns = (749, 813, 878)
        for x, title in zip(columns, ('Better', 'Same', 'Worse')):
            self.label(title, x, 270, 14, color=MUTED, align='right')
        first_run = summary['runs'][0]
        for i, (key, name) in enumerate(QUALITY.items()):
            y = 305 + i * 45
            self.line(636, y - 9, 887, y - 9, LINE)
            self.label(name, 636, y, 15, color=PINE)
            counts = first_run[f'{key}_query_counts']
            for x, status, tint in zip(columns, ('improved', 'tied', 'worsened'), (TEAL, MUTED, RUST)):
                self.label(counts[status], x, y - 2, 17, color=tint, align='right')
        self.paragraph('Each row accounts for all test claims.', 636, 402, 246, 13, MUTED, max_height=32)
        self.box(LEFT, 459, 13, 13, BASE, 2)
        self.label('Vector order', LEFT + 20, 457, 13, 'Helvetica', MUTED)
        self.box(173, 459, 13, 13, TEAL, 2)
        self.label('Reranked', 193, 457, 13, 'Helvetica', MUTED)
        quality_sections = ('baseline', 'reranked', 'quality_delta')
        fixed = all(aggregate[arm][key]['min'] == aggregate[arm][key]['max']
                    for arm in quality_sections for key in QUALITY)
        if fixed:
            note = f'Quality scores were identical across all {summary["run_count"]} passes.'
        else:
            note = 'Pass-level quality ranges are recorded in summary.json.'
        self.label(note, RIGHT, 459, 13, 'Helvetica', MUTED, align='right')
        self.next()

    def latency(self, summary, result_path):
        aggregate = summary['across_runs']
        self.start('Measured CPU latency', 'What does reranking cost per query?',
                   'Warm query latency in milliseconds. Values are median [min–max] across full passes.',
                   f'{result_path.name}/summary.json  /  paired query timings in run-*.json')
        columns = [('Vector top five', 'baseline'), ('Reranked top five', 'reranked'),
                   ('Paired added time', 'added_latency')]
        for i, (label, group) in enumerate(columns):
            x = 172 + i * 244
            self.label(label, x + 15, 179, 17, color=PINE)
            for j, key in enumerate(LATENCY):
                y = 213 + j * 93
                value = aggregate[group][key]
                self.box(x, y, 229, 77, ROSE if group == 'added_latency' else white, 8)
                fmt = '+.1f' if group == 'added_latency' else '.1f'
                self.label(format(value['median'], fmt) + ' ms', x + 15, y + 6,
                           28, color=RUST if group == 'added_latency' else PINE)
                self.label(f"[{value['min']:{fmt}}–{value['max']:{fmt}}] ms", x + 17, y + 48,
                           16, 'Helvetica', MUTED)
        for j, label in enumerate(LATENCY.values()):
            self.label(label, LEFT, 229 + j * 93, 28, color=PINE)
        self.label('How to read this', LEFT, 421, 16, color=PINE)
        self.paragraph('p50 is the median query time. p95 describes the slow tail. For paired added time, subtract '
                       'the two times for each claim before taking percentiles.', LEFT, 445, 827,
                       16, MUTED, leading=18, max_height=38)
        self.next()

    def evidence(self, stats, summary, result_path):
        rows, wins, losses, misses = stats
        cases = [('Promoted', wins, MINT), ('Demoted', losses, ROSE),
                 ('Missing from top 50', misses, white)]
        ceiling = pct(summary['runs'][0]['candidate_pool']['oracle_recall_at_5'])
        self.start('Measurement trace', 'Inspect the ranks behind the means',
                   f'{len(misses)} of {len(rows)} claims had no judged hit in the pool. '
                   f'Perfect ordering caps recall@5 at {ceiling}.',
                   f'{result_path.name}/run-01.json  /  chunk-map.json  /  SciFact via BEIR, CC BY-SA 4.0')
        for i, (heading, selection, color) in enumerate(cases):
            x = LEFT + i * 288
            self.box(x, 176, 271, 255, color, 10)
            self.label(heading, x + 15, 191, 18, color=PINE)
            if selection:
                row, candidate, _, _ = selection[0]
                relevant = set(row['relevant'])
                self.label(f"Claim {row['query_id']}", x + 15, 223, 13)
                self.paragraph(row['query'], x + 15, 249, 240, 16, max_height=100)
                before = first_hit(row['baseline']['docs'], relevant) or 'miss'
                after = first_hit(row['reranked']['docs'], relevant) or 'miss'
                self.label(f'First top-5 hit   {before} → {after}', x + 15, 352, 17, color=PINE)
                self.label(f'Vector parent rank   {candidate or "outside pool"}',
                           x + 15, 389, 13, color=MUTED)
        command = f'make replay RESULTS=results/{result_path.name}'
        self.label(command, LEFT, 449, 15, 'Courier', PINE)
        self.next()

    def ablation(self, summary, result_path):
        base, alt = summary['baseline'], summary['alternative']
        overlap = summary['overlap_tokens']
        self.start('Supplemental chunking experiment', 'What changes with shorter windows?',
                   f'One vector-only pass on the same {summary["query_count"]} test claims. Both windows overlap by {overlap} tokens.',
                   f'{result_path.name}/chunk-ablation/summary.json  /  candidate IDs and scores in observations.json')
        columns = [LEFT, 342, 527, 711]
        self.box(LEFT, 176, RIGHT - LEFT, 48, PINE, 7)
        self.label('MEASURE', columns[0] + 14, 191, 13, color=MINT)
        self.label(f'{base["window_tokens"]}-TOKEN WINDOW', columns[1] + 8, 191, 13,
                   color=white)
        self.label(f'{alt["window_tokens"]}-TOKEN WINDOW', columns[2] + 8, 191, 13,
                   color=white)
        self.label('CHANGE', columns[3] + 8, 191, 13, color=MINT)
        measures = [
            ('Indexed chunks', 'chunks', lambda n: f'{n:,}', lambda n: f'{n:+,}'),
            ('Embedding matrix', 'index_bytes', lambda n: f'{n / 2**20:.2f} MiB',
             lambda n: f'{n / 2**20:+.2f} MiB'),
            ('Top-50 candidate recall', 'pool_recall', pct, points),
            ('MRR@5', 'mrr_at_5', pct, points),
            ('Recall@5', 'recall_at_5', pct, points),
        ]
        for i, (label, key, fmt, delta_fmt) in enumerate(measures):
            y = 224 + i * 36
            self.box(LEFT, y, RIGHT - LEFT, 35, MINT if i % 2 else white)
            self.label(label, columns[0] + 14, y + 7, 17, color=PINE)
            self.label(fmt(base[key]), columns[1] + 8, y + 7, 17, color=INK)
            self.label(fmt(alt[key]), columns[2] + 8, y + 7, 17, color=INK)
            self.label(delta_fmt(alt[key] - base[key]), columns[3] + 8, y + 7, 17,
                       color=PINE)
        base_stride, alt_stride = base['window_tokens'] - overlap, alt['window_tokens'] - overlap
        self.label(f'Stride changes from {base_stride} to {alt_stride} tokens.', LEFT, 417, 17, color=PINE)
        self.paragraph('The result covers vector quality and embedding matrix size. Chunking latency and '
                       'interaction with reranking remain open.', LEFT, 445, 821,
                       15, MUTED, leading=17, max_height=35)
        self.next()

    def callouts(self, items):
        for i, (heading, content) in enumerate(items):
            x = LEFT + (i % 2) * 433
            y = 177 + (i // 2) * 149
            self.box(x, y, 415, 132, white, 9)
            self.box(x + 16, y + 18, 5, 24, TEAL)
            self.label(heading, x + 33, y + 16, 21, color=PINE)
            self.paragraph(content, x + 33, y + 52, 358, 16, MUTED, max_height=69)

    def limits(self):
        self.start('Limits and failure modes', 'Where retrieval can fall short',
                   'Follow the evidence from the candidate pool to the production workload.',
                   'SciFact document judgments  /  run-01.json  /  REPORT.md')
        self.callouts([
            ('Candidate coverage', 'A topical match can occupy a slot while a relevant parent stays outside the '
             'top 50. A reranker can only reorder the available chunks.'),
            ('Ranking errors', 'Joint scoring can demote a judged relevant result. We evaluated one model pair '
             'and one scientific-abstract corpus.'),
            ('Document-level labels', 'A relevant parent may contain evidence in a different chunk. Unjudged '
             'parents receive zero credit. Evidence can support or refute a claim.'),
            ('Serving conditions', 'The benchmark uses warm, sequential CPU queries. Cold starts, concurrency, '
             'other hardware and answer quality require separate evaluation.'),
        ])
        self.next()

    def decision(self, aggregate):
        cost = aggregate['reranked']['p95_ms']['median']
        mrr = aggregate['quality_delta']['mrr_at_5']['median']
        recall = aggregate['quality_delta']['recall_at_5']['median']
        self.start('Recommendation', 'Use a measured retrieval budget',
                   'Compare the observed evidence ranking and tail latency against the needs of the workload.',
                   'Primary references and versioned dependencies in docs/SOURCES.md')
        if mrr > 0 and recall > 0:
            recommendation = ('Rerank selectively',
                              f'Both metrics improved at an observed retrieval p95 of {cost:.1f} ms. '
                              'Keep vector order if the retrieval budget is tighter.')
        elif mrr <= 0 and recall <= 0:
            recommendation = ('Keep vector order for SciFact',
                              f'Both quality measures stayed flat or fell. Reranking reached {cost:.1f} ms at p95 '
                              'on this CPU.')
        else:
            recommendation = ('Prioritize the metric you need',
                              f'MRR@5 changed by {points(mrr)} and recall@5 by {points(recall)}. '
                              f'Reranking reached {cost:.1f} ms at p95 on this CPU.')
        items = [
            recommendation,
            ('Inspect the candidate pool', 'If judged evidence rarely reaches the pool, improve first-stage '
             'retrieval. Shorter windows trade measurable ranking gains for additional matrix storage here.'),
            ('Validate on the target workload', 'Test candidate depth, passage-level evidence and serving load. '
             'Track retrieval quality and tail latency on the intended hardware.'),
        ]
        for i, (heading, description) in enumerate(items):
            y = 181 + i * 94
            self.line(LEFT, y, RIGHT, y)
            self.label(heading, LEFT, y + 15, 20, color=PINE)
            self.paragraph(description, 384, y + 15, 500, 17, MUTED, max_height=71)
        self.next()

    def reproducibility(self, environment, result_path):
        self.start('Appendix / Reproducibility', 'From a fresh clone to raw evidence',
                   'Linux or WSL x86-64 with CPython 3.12. Preparation downloads inputs. Measurement runs offline.',
                   'README.md  /  requirements.txt  /  environment.json')
        config = environment['config']
        self.box(LEFT, 175, 365, 201, PINE, 9)
        self.label('FULL STUDY', LEFT + 17, 190, 13, color=MINT)
        commands = (
            ('make setup', 'Install the hash-locked CPU environment'),
            ('make prepare', 'Fetch pinned inputs and build chunks'),
            ('make study', 'Measure the primary and supplemental study'),
        )
        for i, (command, explanation) in enumerate(commands):
            y = 220 + i * 49
            self.label(command, LEFT + 17, y, 16, 'Courier-Bold', white)
            self.label(explanation, LEFT + 17, y + 21, 13, 'Helvetica', MINT)
        self.label('PINNED INPUTS', 449, 183, 13, color=TEAL)
        pinned = (
            ('Corpus and queries', config['dataset']['id'], config['dataset']['revision']),
            ('Test judgments', config['dataset']['qrels_id'], config['dataset']['qrels_revision']),
            ('Bi-encoder', config['embedding']['id'].split('/')[-1], config['embedding']['revision']),
            ('Cross-encoder', config['reranker']['id'].split('/')[-1], config['reranker']['revision']),
        )
        for i, (label, model, revision) in enumerate(pinned):
            y = 215 + i * 39
            self.line(449, y - 7, RIGHT, y - 7)
            self.label(label, 449, y, 14, color=PINE)
            self.label(f'{model} @{revision[:7]}', 615, y, 14, 'Helvetica', MUTED)
        self.line(LEFT, 397, RIGHT, 397)
        self.label(f'make replay RESULTS=results/{result_path.name}', LEFT, 410, 15,
                   'Courier', PINE)
        self.paragraph('Replay verifies rankings and recomputes metrics from stored observations. '
                       'Version and input hashes are recorded in the run environment.', LEFT, 442,
                       808, 15, MUTED, max_height=41)
        self.next()

    def tuning(self):
        self.start('Appendix / Follow-up experiments', 'Tune for the failure you observe',
                   'Proposed experiments. Hold other settings fixed, then measure the quality and cost of each change.',
                   'Study controls in REPORT.md  /  Sentence Transformers retrieve-and-rerank guide')
        columns = (LEFT + 15, 282, 607)
        self.box(LEFT, 177, RIGHT - LEFT, 40, PINE, 7)
        for x, label in zip(columns, ('SYMPTOM', 'CHANGE TO TEST', 'WHAT TO MEASURE')):
            self.label(label, x, 189, 13, color=white)
        proposals = (
            ('Evidence absent from pool', 'Increase candidate depth or add a lexical candidate source.',
             'Candidate recall, the top-five quality scores, and added p95.'),
            ('Chunks miss context', 'Compare window sizes, overlap, and sentence boundaries.',
             'Passage-level evidence, matrix size, and retrieval time.'),
            ('Reranking exceeds budget', 'Try selective reranking or a smaller scorer.',
             'Tail latency and quality on the queries where it runs.'),
            ('Deployment behavior shifts', 'Run the chosen variant at the target load and hardware.',
             'Cold starts, concurrent p95, and generated-answer grounding.'),
        )
        for i, (symptom, experiment, measurement) in enumerate(proposals):
            y = 217 + 63 * i
            self.box(LEFT, y, RIGHT - LEFT, 62, MINT if i % 2 else white)
            self.paragraph(symptom, columns[0], y + 11, 198, 15, PINE, max_height=48)
            self.paragraph(experiment, columns[1], y + 11, 290, 15, MUTED, max_height=48)
            self.paragraph(measurement, columns[2], y + 11, 268, 15, MUTED, max_height=48)
        self.next()

    def questions(self):
        self.start('Appendix / Q&A', 'Explain the evidence behind the score',
                   'Four distinctions to use when interpreting document retrieval results.',
                   'SciFact and BEIR documentation  /  Lewis et al. (2020)  /  REPORT.md')
        self.callouts([
            ('What counts as a hit?', 'A judged relevant parent abstract in the five unique results. '
             'Overlapping chunks from that abstract cannot earn extra credit.'),
            ('Does relevance prove truth?', 'A judged abstract can support or refute the claim. '
             'The ranking measures whether the abstract is useful evidence.'),
            ('Why stop before generation?', 'The experiment isolates retrieval. Answer correctness and grounding '
             'would require a generator, prompts and a separate evaluation.'),
            ('What does replay prove?', 'Replay validates the recorded candidate pools and rank calculations, '
             'then recomputes scores and timing summaries from the saved logs.'),
        ])
        self.next()

    def sources(self):
        self.start('Appendix / Sources', 'Read the primary sources',
                   'Select a card to open its source. Dataset and model revisions are recorded in the repository.',
                   'Complete citations, package releases and SciFact attribution in docs/SOURCES.md')
        references = (
            ('RAG', 'Lewis et al. (2020)', 'Retrieval-augmented generation with retrieved context.',
             'https://arxiv.org/abs/2005.11401'),
            ('SciFact', 'Wadden et al. (2020)', 'Scientific claims, evidence abstracts and judgments.',
             'https://aclanthology.org/2020.emnlp-main.609/'),
            ('BEIR', 'Thakur et al. (2021)', 'A benchmark for zero-shot retrieval evaluation.',
             'https://arxiv.org/abs/2104.08663'),
            ('Retrieve and rerank', 'Sentence Transformers', 'Bi-encoder candidate retrieval and cross-encoder scoring.',
             'https://www.sbert.net/examples/sentence_transformer/applications/retrieve_rerank/README.html'),
            ('Chunking strategies', 'Qu et al. (2025)', 'Evaluation of fixed-size and semantic splitting.',
             'https://aclanthology.org/2025.findings-naacl.114/'),
            ('Pinned embedding model', 'MiniLM-L6-v2 model card', 'Encoder input limit and model configuration.',
             'https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/blob/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/README.md'),
        )
        for i, (heading, attribution, body, url) in enumerate(references):
            x = LEFT + (i % 3) * 288
            y = 175 + (i // 3) * 151
            self.box(x, y, 271, 130, white, 8)
            self.label(heading, x + 15, y + 13, 17, color=PINE)
            self.label(attribution, x + 15, y + 40, 14, color=TEAL)
            self.paragraph(body, x + 15, y + 66, 235, 14, MUTED, max_height=50)
            self.canvas.linkURL(url, (x, HEIGHT - y - 130, x + 271, HEIGHT - y), relative=0)
        self.next()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--results', type=Path, help='Complete five-pass benchmark directory')
    output = parser.add_mutually_exclusive_group()
    output.add_argument('--report-only', action='store_true')
    output.add_argument('--slides-only', action='store_true')
    args = parser.parse_args()
    if not args.report_only and not args.results:
        parser.error('--results is required to render the slides')
    if not args.slides_only:
        render_report()
    if args.report_only:
        return
    summary = read_json(args.results / 'summary.json')
    environment = read_json(args.results / 'environment.json')
    if environment['pilot'] or summary['fixture_only'] or summary['run_count'] < 5:
        parser.error('Slide data must come from a full benchmark with five or more passes')
    chunking = read_json(args.results / 'chunk-ablation' / 'summary.json')
    stats = diagnostics(args.results)
    deck = Slides()
    deck.cover(summary['across_runs'])
    deck.workflow()
    deck.pipeline()
    deck.chunking()
    deck.protocol(environment, summary)
    deck.metrics_example()
    deck.quality(summary, args.results)
    deck.latency(summary, args.results)
    deck.evidence(stats, summary, args.results)
    deck.ablation(chunking, args.results)
    deck.limits()
    deck.decision(summary['across_runs'])
    deck.reproducibility(environment, args.results)
    deck.tuning()
    deck.questions()
    deck.sources()
    deck.canvas.save()
    export_display_values(args.results, environment, summary, chunking, stats)


if __name__ == '__main__':
    main()
