import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../design/theme.dart';
import 'app_controller.dart';
import 'router.dart';

/// Root widget. Themes the app from the stored profile and wires the router.
class ZanyTestPrepApp extends ConsumerWidget {
  const ZanyTestPrepApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final async = ref.watch(appControllerProvider);
    final themeMode = async.valueOrNull?.profile?.themeMode ?? ThemeMode.system;

    // While bootstrapping (loading content + storage), show a branded splash.
    if (async.isLoading) {
      return MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(),
        darkTheme: AppTheme.dark(),
        themeMode: themeMode,
        home: const _Splash(),
      );
    }
    if (async.hasError) {
      return MaterialApp(
        debugShowCheckedModeBanner: false,
        theme: AppTheme.light(),
        darkTheme: AppTheme.dark(),
        home: Scaffold(
          body: Center(
            child: Padding(
              padding: kPagePadding,
              child: Text(
                'Could not load content.\n${async.error}',
                textAlign: TextAlign.center,
              ),
            ),
          ),
        ),
      );
    }

    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      debugShowCheckedModeBanner: false,
      title: 'Zany Test Prep',
      theme: AppTheme.light(),
      darkTheme: AppTheme.dark(),
      themeMode: themeMode,
      routerConfig: router,
    );
  }
}

class _Splash extends StatelessWidget {
  const _Splash();

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school_rounded, size: 72, color: scheme.primary),
            Gap.m,
            Text(
              'Zany Test Prep',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            Gap.l,
            const CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}
