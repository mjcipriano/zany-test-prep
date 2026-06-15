import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../features/achievements/achievements_screen.dart';
import '../features/home/home_screen.dart';
import '../features/lessons/lesson_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/progress/skills_screen.dart';
import '../features/review/review_screen.dart';
import '../features/settings/about_screen.dart';
import '../features/settings/settings_screen.dart';
import 'app_controller.dart';

/// The app router. Redirects to onboarding until a local profile exists.
final routerProvider = Provider<GoRouter>((ref) {
  final refresh = ValueNotifier<int>(0);
  ref.listen(appControllerProvider, (_, __) => refresh.value++);
  ref.onDispose(refresh.dispose);

  return GoRouter(
    initialLocation: '/home',
    refreshListenable: refresh,
    redirect: (context, state) {
      final async = ref.read(appControllerProvider);
      if (async.isLoading || async.hasError) return null;
      final onboarded = async.valueOrNull?.onboarded ?? false;
      final loc = state.matchedLocation;
      if (!onboarded && loc != '/onboarding') return '/onboarding';
      if (onboarded && loc == '/onboarding') return '/home';
      return null;
    },
    routes: [
      GoRoute(
        path: '/onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),
      GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
      GoRoute(
        path: '/lesson/:id',
        builder: (context, state) => LessonScreen(
          lessonId: state.pathParameters['id']!,
          reviewMode: state.uri.queryParameters['review'] == 'true',
        ),
      ),
      GoRoute(
        path: '/review',
        builder: (context, state) => const ReviewScreen(),
      ),
      GoRoute(
        path: '/skills',
        builder: (context, state) => const SkillsScreen(),
      ),
      GoRoute(
        path: '/achievements',
        builder: (context, state) => const AchievementsScreen(),
      ),
      GoRoute(
        path: '/settings',
        builder: (context, state) => const SettingsScreen(),
      ),
      GoRoute(path: '/about', builder: (context, state) => const AboutScreen()),
    ],
  );
});
