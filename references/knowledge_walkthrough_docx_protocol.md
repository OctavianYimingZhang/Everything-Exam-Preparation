# Knowledge Walkthrough DOCX Protocol

`knowledge_walkthrough_docx` is a compatibility route for users who explicitly ask for a lecture/source-order walkthrough. It writes the same artifact:

```text
Lecture_Knowledge_Walkthrough.docx
```

The route uses the same `PublicLectureNotesPlan`, validator, exam-ready direct prose gate, module teaching depth gate, readability layout gate and DOCX renderer as `exam_prep_notes_docx`. The only difference is that the style profile route is `knowledge_walkthrough_docx` and source/session order is treated as the primary ordering signal.

## Contract

Required public shape:

```yaml
PublicLectureNotesPlan:
  title:
  target_group_key:
  source_scale_budget:
  output_language_profile:
  route_docx_style_profile:
    route: knowledge_walkthrough_docx
    margin_cm: 2.0
    line_spacing: 1.05-1.15
    body_alignment: left
    title_alignment: left
    heading_alignment: left
    image_alignment: center
    text_color: black
    theme_colours_allowed: false
    blue_heading_styles_allowed: false
  public_lecture_sections:
    - lecture_title:
      modules:
        - module_title:
          knowledge_functions:
          explanation:
          blocks:
```

Legacy `course_modules`, `legacy_lectures`, `Course Knowledge Map` and knowledge-card scaffolds are internal-only compatibility inputs. They must be converted into `public_lecture_sections` before public DOCX writing or the run fails.

## Student Surface

The public document starts with the title and then lecture headings. It does not include a source role summary, source scope, extraction limitation, course map, prediction, study order, answer strategy, Section A/B strategy, or `How To Use This Document`.

Each module must explain at least two knowledge functions from definition/boundary, mechanism/process, method/readout, graph/data interpretation, calculation/unit/worked example, named example, and limitation/trap. The output should teach concept -> why it matters -> how it works -> interpretation -> boundary.

A walkthrough module must still be a micro-module teaching note, not a record of what the source says. Use direct knowledge claims and block release for wording such as `The course frames`, `The lecture states`, `The source material identifies`, `The source states`, or equivalent source narration. If a source-order section contains several separable operations, split it into smaller module headings.

## Language And Style

Default public output is English unless the user explicitly asks for Chinese or bilingual notes. Lecture walkthroughs use the ordinary notes style: black Arial, 2.0 cm margins, compact 1.05-1.15 line spacing, left-aligned body and headings, centered images, no theme colours and no blue heading styles.

## QA Gate

Block and regenerate if the DOCX contains raw slide bullets, source_route_narration, source narration, ai_process_or_provenance, internal QA fields, evidence scores, confidence bands, strategy/prediction content, inventory-only prose, missing module teaching depth, over-dense readability layout, repeated rigid labels, colon-slot fragmentation, shorthand arrow chains, non-black text, non-Arial text, justified body text or non-compact spacing.
