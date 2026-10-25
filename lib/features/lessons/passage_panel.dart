import 'package:flutter/material.dart';

import '../../design/theme.dart';
import '../../domain/models/question.dart';

/// Phone layout for ACT-length passages ([Stimulus.isLongPassage]).
///
/// A 700-word passage stacked above the question would push the prompt and
/// choices several screens down, and the reader would scroll past it again on
/// every one of the set's nine questions. Instead the passage sits in a
/// height-capped card with its own scrollbar, so the question stays in view
/// right below it, and its paragraphs are numbered to match the "paragraph N"
/// references in the questions. The expand button opens the whole passage in a
/// full-height sheet for comfortable reading.
///
/// The scroll position is stored per passage (PageStorage), so moving between
/// questions of the same set keeps the reader's place.
class LongPassagePanel extends StatefulWidget {
  const LongPassagePanel({super.key, required this.stimulus});

  final Stimulus stimulus;

  /// Height of the scrollable passage window for a screen of [screenHeight]:
  /// about a third of the screen, so the prompt and first choice show below.
  static double windowHeight(double screenHeight) =>
      (screenHeight * 0.36).clamp(200.0, 420.0);

  @override
  State<LongPassagePanel> createState() => _LongPassagePanelState();
}

class _LongPassagePanelState extends State<LongPassagePanel> {
  final _scroll = ScrollController();

  @override
  void dispose() {
    _scroll.dispose();
    super.dispose();
  }

  String get _storageId {
    final s = widget.stimulus;
    return 'passage-${Object.hash(s.title, s.text, s.textB)}';
  }

  String get _title =>
      widget.stimulus.title ??
      (widget.stimulus.isPaired ? 'Paired passages' : 'Passage');

  void _openFullScreen() {
    showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      useSafeArea: true,
      showDragHandle: true,
      builder: (context) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.95,
        minChildSize: 0.5,
        maxChildSize: 1,
        builder: (context, controller) => ListView(
          key: const Key('passage-sheet'),
          controller: controller,
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
          children: [
            Row(
              children: [
                Expanded(child: _Title(title: _title)),
                IconButton(
                  tooltip: 'Back to the question',
                  icon: const Icon(Icons.close_rounded),
                  onPressed: () => Navigator.of(context).pop(),
                ),
              ],
            ),
            Gap.s,
            PassageBody(stimulus: widget.stimulus),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final height = LongPassagePanel.windowHeight(
      MediaQuery.sizeOf(context).height,
    );
    return Material(
      color: scheme.surfaceContainer,
      borderRadius: BorderRadius.circular(20),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 6, 4, 0),
            child: Row(
              children: [
                Icon(Icons.menu_book_rounded, size: 18, color: scheme.primary),
                const SizedBox(width: 8),
                Expanded(child: _Title(title: _title)),
                IconButton(
                  key: const Key('passage-expand'),
                  tooltip: 'Read the full passage',
                  icon: const Icon(Icons.open_in_full_rounded, size: 20),
                  onPressed: _openFullScreen,
                ),
              ],
            ),
          ),
          SizedBox(
            height: height,
            child: Scrollbar(
              controller: _scroll,
              thumbVisibility: true,
              child: SingleChildScrollView(
                key: PageStorageKey<String>(_storageId),
                controller: _scroll,
                padding: const EdgeInsets.fromLTRB(16, 4, 20, 16),
                child: PassageBody(stimulus: widget.stimulus),
              ),
            ),
          ),
          Container(
            padding: const EdgeInsets.fromLTRB(16, 6, 16, 8),
            color: scheme.surfaceContainerHigh,
            child: Text(
              '${widget.stimulus.wordCount} words · scroll here or expand '
              'to read full screen',
              style: Theme.of(
                context,
              ).textTheme.labelSmall?.copyWith(color: scheme.onSurfaceVariant),
            ),
          ),
        ],
      ),
    );
  }
}

class _Title extends StatelessWidget {
  const _Title({required this.title});
  final String title;

  @override
  Widget build(BuildContext context) {
    return Text(
      title,
      maxLines: 2,
      overflow: TextOverflow.ellipsis,
      style: Theme.of(context).textTheme.labelLarge?.copyWith(
        color: Theme.of(context).colorScheme.primary,
        fontWeight: FontWeight.w800,
      ),
    );
  }
}

/// The passage text with numbered paragraphs; paired passages get a
/// "Passage A" / "Passage B" heading each, numbered from 1 within each text.
class PassageBody extends StatelessWidget {
  const PassageBody({super.key, required this.stimulus});

  final Stimulus stimulus;

  @override
  Widget build(BuildContext context) {
    if (!stimulus.isPaired) {
      return _Paragraphs(paragraphs: stimulus.paragraphs);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const _Heading('Passage A'),
        _Paragraphs(paragraphs: stimulus.paragraphs),
        Gap.s,
        const _Heading('Passage B'),
        _Paragraphs(paragraphs: stimulus.paragraphsB),
      ],
    );
  }
}

class _Heading extends StatelessWidget {
  const _Heading(this.text);
  final String text;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 6, bottom: 8),
      child: Text(
        text,
        style: Theme.of(context).textTheme.titleSmall?.copyWith(
          fontWeight: FontWeight.w800,
          letterSpacing: 0.3,
        ),
      ),
    );
  }
}

class _Paragraphs extends StatelessWidget {
  const _Paragraphs({required this.paragraphs});
  final List<String> paragraphs;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        for (final (i, p) in paragraphs.indexed)
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(
                  width: 22,
                  child: Text(
                    '${i + 1}',
                    semanticsLabel: 'Paragraph ${i + 1}',
                    style: TextStyle(
                      fontSize: 12,
                      height: 2,
                      fontWeight: FontWeight.w800,
                      color: scheme.primary,
                    ),
                  ),
                ),
                Expanded(
                  child: Text(
                    p,
                    style: const TextStyle(fontSize: 15.5, height: 1.5),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }
}
