# EasyPiper - Detailed Task List for Next Iteration

This document outlines all identified inconsistencies, issues, and improvement opportunities in the EasyPiper codebase. Tasks are categorized by priority and area.

**Last Updated:** 2025-11-05  
**Generated From:** Comprehensive codebase analysis

---

## ✅ Completed Tasks

### High Priority (Completed)
- [x] Create missing SETUP_GUIDE.md file
- [x] Add missing convenience API methods (move_joints, switch_mode_cartesian, move_tcp_pose, gripper_open, gripper_close, gripper_set_position)
- [x] Create pyproject.toml for modern Python packaging
- [x] Add .flake8 configuration file
- [x] Create pytest.ini configuration
- [x] Add basic unit tests for API consistency
- [x] Fix typo in can_activate.sh error message
- [x] Create CI/CD pipeline (.github/workflows/ci.yml)
- [x] Add .gitattributes for proper line endings
- [x] Create requirements-dev.txt

---

## 🔴 High Priority Tasks

### Documentation

#### TASK-DOC-001: Update author_email in setup.py
**Priority:** High  
**File:** `setup.py`  
**Issue:** Line 18 has empty author_email  
**Solution:**
```python
author_email='charith@example.com',  # Add actual email
```

#### TASK-DOC-002: Add badges to README.md
**Priority:** High  
**File:** `README.md`  
**Issue:** Missing CI, test coverage, and version badges  
**Solution:** Add badges after title:
```markdown
[![CI](https://github.com/charithmu/easy_piper/workflows/CI/badge.svg)](...)
[![codecov](https://codecov.io/gh/charithmu/easy_piper/branch/main/graph/badge.svg)](...)
[![PyPI version](https://badge.fury.io/py/easy-piper.svg)](...)
```

### Code Quality

#### TASK-CODE-001: Add comprehensive type hints
**Priority:** High  
**Files:** All Python files in `src/easy_piper/`  
**Issue:** Type hints are partial or missing  
**Solution:**
- Add type hints to all function signatures
- Add return type annotations
- Use `typing.Optional`, `typing.Union`, etc. properly
- Target Python 3.7+ type hint syntax

**Examples:**
```python
# Before
def move_joints(self, angles_deg):
    ...

# After  
def move_joints(self, angles_deg: Sequence[float]) -> None:
    ...
```

#### TASK-CODE-002: Improve error messages
**Priority:** High  
**Files:** `src/easy_piper/easy_piper.py`, `src/easy_piper/piper_recorder.py`  
**Issue:** Some error messages lack context or suggestions  
**Solution:**
- Add more descriptive error messages
- Include resolution hints in error messages
- Use custom exception classes for different error types

**Example:**
```python
# Before
raise ValueError("pose must have 6 elements")

# After
raise ValueError(
    "pose must have 6 elements [X, Y, Z, RX, RY, RZ], "
    f"but got {len(pose)} elements"
)
```

#### TASK-CODE-003: Add input validation
**Priority:** High  
**Files:** All methods accepting user input  
**Issue:** Some methods don't validate input ranges  
**Solution:**
- Validate joint angles are within reasonable ranges
- Validate gripper positions and efforts
- Validate speed percentages (0-100)
- Add clear error messages for out-of-range values

---

## 🟡 Medium Priority Tasks

### Code Organization

#### TASK-ORG-001: Extract constants to module-level
**Priority:** Medium  
**Files:** `src/easy_piper/piper_recorder.py`  
**Issue:** Magic numbers throughout code (camera indices: 6, 4; resolutions: 1280, 720, 2560)  
**Solution:**
```python
# Add at top of file
CAMERA_ZED_INDEX = 6
CAMERA_ORBBEC_INDEX = 4
CAMERA_ZED_WIDTH = 2560
CAMERA_ZED_HEIGHT = 720
CAMERA_ORBBEC_WIDTH = 1280
CAMERA_ORBBEC_HEIGHT = 720
DEFAULT_RECORDING_FPS = 30
```

#### TASK-ORG-002: Create custom exception classes
**Priority:** Medium  
**File:** `src/easy_piper/exceptions.py` (new file)  
**Issue:** Uses generic exceptions everywhere  
**Solution:**
```python
class EasyPiperError(Exception):
    """Base exception for EasyPiper."""
    pass

class CANSetupError(EasyPiperError):
    """CAN device setup failed."""
    pass

class RobotConnectionError(EasyPiperError):
    """Failed to connect to robot."""
    pass

class InvalidParameterError(EasyPiperError):
    """Invalid parameter provided."""
    pass
```

#### TASK-ORG-003: Split large files
**Priority:** Medium  
**File:** `src/easy_piper/easy_piper.py` (1328 lines)  
**Issue:** Single file is too large  
**Solution:** Consider splitting into:
- `easy_piper/core.py` - Main EasyPiper class
- `easy_piper/can_utils.py` - CAN device utilities
- `easy_piper/conversions.py` - Unit conversion functions

### Testing

#### TASK-TEST-001: Add integration tests
**Priority:** Medium  
**File:** `tests/test_integration.py` (new file)  
**Issue:** Only unit tests exist  
**Solution:** Add integration tests that:
- Test CAN device detection (mocked)
- Test mode switching sequences
- Test trajectory recording workflow
- Mark with `@pytest.mark.integration` decorator

#### TASK-TEST-002: Add hardware tests
**Priority:** Medium  
**File:** `tests/test_hardware.py` (new file)  
**Issue:** No tests for actual hardware  
**Solution:** Add hardware tests that:
- Connect to real robot (if available)
- Test basic movements
- Test data streaming
- Mark with `@pytest.mark.hardware` decorator
- Document how to run with `pytest -m hardware`

#### TASK-TEST-003: Increase test coverage
**Priority:** Medium  
**Files:** All test files  
**Current:** ~30% estimated coverage  
**Target:** 80%+ coverage  
**Solution:**
- Add tests for error conditions
- Add tests for edge cases
- Add tests for CAN utilities
- Add tests for unit conversions

### Documentation

#### TASK-DOC-003: Add docstring examples
**Priority:** Medium  
**Files:** All Python files  
**Issue:** Many docstrings lack usage examples  
**Solution:** Add examples to docstrings:
```python
def move_tcp_pose(self, pose, ...):
    """Move to TCP pose.
    
    Examples:
        >>> arm = EasyPiper()
        >>> arm.move_tcp_pose([300, 0, 400, 180, 0, 0])
    """
```

#### TASK-DOC-004: Create API reference documentation
**Priority:** Medium  
**Files:** `docs/api/` (new directory)  
**Issue:** No generated API documentation  
**Solution:**
- Use Sphinx to generate API docs
- Add to CI pipeline
- Host on GitHub Pages or ReadTheDocs

#### TASK-DOC-005: Add more examples
**Priority:** Medium  
**Files:** `examples/` directory  
**Issue:** Limited examples for advanced features  
**Solution:** Add examples for:
- Multi-arm coordination
- Trajectory recording with cameras
- MIT mode control
- Error recovery
- Master-slave configuration

---

## 🟢 Low Priority Tasks

### Code Quality

#### TASK-QUALITY-001: Add pre-commit hooks
**Priority:** Low  
**File:** `.pre-commit-config.yaml` (new file)  
**Solution:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
```

#### TASK-QUALITY-002: Add shellcheck compliance
**Priority:** Low  
**Files:** `scripts/*.sh`  
**Issue:** Shell scripts not validated with shellcheck  
**Solution:**
- Run shellcheck on all .sh files
- Fix any warnings
- Add shellcheck to CI pipeline

#### TASK-QUALITY-003: Improve camera handling robustness
**Priority:** Low  
**File:** `src/easy_piper/piper_recorder.py`  
**Issue:** Camera handling could be more robust  
**Solution:**
- Add camera reconnection logic
- Handle camera disconnection gracefully
- Add camera health checks
- Support different camera models/indices

### Features

#### TASK-FEAT-001: Add logging support
**Priority:** Low  
**Files:** All Python files  
**Issue:** Uses print() instead of logging  
**Solution:**
- Replace print() with logging
- Add configurable log levels
- Add file logging option
- Example:
```python
import logging
logger = logging.getLogger(__name__)
logger.info("Connected to robot")
```

#### TASK-FEAT-002: Add configuration file support
**Priority:** Low  
**File:** `config.yaml` or `easy_piper.conf`  
**Issue:** All configuration is hardcoded  
**Solution:** Support configuration files for:
- Default CAN device name
- Camera indices and settings
- Recording parameters
- Robot TCP zero pose

#### TASK-FEAT-003: Add telemetry/metrics
**Priority:** Low  
**Files:** `src/easy_piper/metrics.py` (new file)  
**Solution:**
- Track robot usage statistics
- Monitor performance metrics
- Export metrics in standard formats
- Optional prometheus integration

### Documentation

#### TASK-DOC-006: Add architecture diagram
**Priority:** Low  
**File:** `docs/ARCHITECTURE.md`  
**Solution:** Document:
- System architecture
- Component interactions
- Data flow
- CAN communication protocol

#### TASK-DOC-007: Add video tutorials
**Priority:** Low  
**Files:** Links in README  
**Solution:**
- Record setup video
- Record basic usage video
- Record advanced features video
- Host on YouTube

---

## 📋 Testing Checklist

For each task, verify:
- [ ] Code changes implemented
- [ ] Tests added/updated
- [ ] Tests passing locally
- [ ] Documentation updated
- [ ] CI passing
- [ ] Code reviewed
- [ ] Merged to main branch

---

## 🎯 Next Sprint Planning

### Sprint 1 (Week 1-2)
Focus: Code Quality & Testing
- TASK-CODE-001: Add type hints
- TASK-CODE-002: Improve error messages
- TASK-TEST-001: Add integration tests
- TASK-TEST-003: Increase test coverage
- TASK-DOC-001: Update author_email

### Sprint 2 (Week 3-4)
Focus: Documentation & Organization  
- TASK-ORG-001: Extract constants
- TASK-DOC-002: Add badges
- TASK-DOC-003: Add docstring examples
- TASK-DOC-004: Create API reference
- TASK-QUALITY-001: Add pre-commit hooks

### Sprint 3 (Week 5-6)
Focus: Features & Improvements
- TASK-ORG-002: Create custom exceptions
- TASK-CODE-003: Add input validation
- TASK-TEST-002: Add hardware tests
- TASK-FEAT-001: Add logging support
- TASK-DOC-005: Add more examples

---

## 📊 Metrics & Goals

### Code Quality Metrics
- **Test Coverage:** Current ~30% → Target 80%+
- **Type Hint Coverage:** Current ~40% → Target 95%+
- **Documentation Coverage:** Current ~60% → Target 90%+
- **Flake8 Compliance:** Current ~85% → Target 100%
- **MyPy Compliance:** Current ~50% → Target 90%+

### Development Metrics
- **CI Success Rate:** Target 100%
- **Average PR Review Time:** Target < 24 hours
- **Issue Resolution Time:** Target < 7 days
- **Documentation Freshness:** Target < 30 days

---

## 🤝 Contributing

When implementing tasks:
1. Reference task ID in commit messages (e.g., "TASK-CODE-001: Add type hints to EasyPiper class")
2. Update this file when tasks are completed
3. Add tests for all changes
4. Update documentation as needed
5. Request code review before merging

---

## 📝 Notes

- This list is living and should be updated as new issues are discovered
- Priority levels may change based on user feedback
- Some tasks may be split into smaller subtasks during implementation
- Consider user impact when prioritizing tasks

---

**Document Version:** 1.0  
**Last Reviewed:** 2025-11-05  
**Maintained By:** EasyPiper Core Team
