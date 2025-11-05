"""
Tests for EasyPiper API consistency and basic functionality.

These tests verify that the API matches the documentation and examples
without requiring actual hardware.
"""

import sys
import pytest
from unittest.mock import Mock, patch, MagicMock

# Mock dependencies before importing easy_piper
sys.modules['piper_sdk'] = Mock()
sys.modules['cv2'] = Mock()

from easy_piper import EasyPiper


class TestEasyPiperAPI:
    """Test EasyPiper API methods exist and have correct signatures."""

    @pytest.fixture
    def mock_piper_interface(self):
        """Create a mock C_PiperInterface_V2 for testing."""
        mock_iface = Mock()
        mock_iface.get_connect_status.return_value = True
        mock_iface.GetArmJointMsgs.return_value = Mock(
            joint_state=Mock(
                joint_1=0, joint_2=0, joint_3=0,
                joint_4=0, joint_5=0, joint_6=0
            ),
            Hz=50.0
        )
        mock_iface.GetArmGripperMsgs.return_value = Mock(
            gripper_state=Mock(grippers_angle=0, grippers_effort=0),
            Hz=50.0
        )
        mock_iface.GetArmEndPoseMsgs.return_value = Mock(
            end_pose=Mock(
                X_axis=56127, Y_axis=0, Z_axis=213266,
                RX_axis=0, RY_axis=84999, RZ_axis=0
            ),
            Hz=50.0
        )
        return mock_iface

    @pytest.fixture
    def easy_piper(self, mock_piper_interface):
        """Create EasyPiper instance with mocked interface."""
        with patch('easy_piper.easy_piper.C_PiperInterface_V2', return_value=mock_piper_interface):
            with patch('easy_piper.easy_piper._check_can_device_up', return_value=True):
                arm = EasyPiper(auto_setup_can=False)
                return arm

    def test_module_imports(self):
        """Test that main classes can be imported."""
        from easy_piper import EasyPiper, LeRobotDataRecorder
        assert EasyPiper is not None
        assert LeRobotDataRecorder is not None

    def test_convenience_methods_exist(self, easy_piper):
        """Test that convenience methods from README examples exist."""
        # Joint methods
        assert hasattr(easy_piper, 'move_joints')
        assert callable(easy_piper.move_joints)
        
        # Cartesian methods
        assert hasattr(easy_piper, 'switch_mode_cartesian')
        assert callable(easy_piper.switch_mode_cartesian)
        
        assert hasattr(easy_piper, 'move_tcp_pose')
        assert callable(easy_piper.move_tcp_pose)
        
        # Gripper methods
        assert hasattr(easy_piper, 'gripper_open')
        assert callable(easy_piper.gripper_open)
        
        assert hasattr(easy_piper, 'gripper_close')
        assert callable(easy_piper.gripper_close)
        
        assert hasattr(easy_piper, 'gripper_set_position')
        assert callable(easy_piper.gripper_set_position)

    def test_move_joints_signature(self, easy_piper):
        """Test move_joints accepts list of 6 angles."""
        # Should accept 6 angles
        easy_piper.move_joints([0, 30, -60, 0, 90, 0])
        easy_piper.iface.JointCtrl.assert_called()
        
        # Should raise error for wrong number of angles
        with pytest.raises(ValueError):
            easy_piper.move_joints([0, 30, -60])

    def test_switch_mode_cartesian(self, easy_piper):
        """Test switch_mode_cartesian switches to cartesian mode."""
        # Default should be linear mode
        easy_piper.switch_mode_cartesian(speed_percent=20)
        easy_piper.iface.ModeCtrl.assert_called()
        
        # Can specify mode explicitly
        easy_piper.switch_mode_cartesian(speed_percent=20, mode='P')
        easy_piper.iface.ModeCtrl.assert_called()
        
        # Invalid mode should raise error
        with pytest.raises(ValueError):
            easy_piper.switch_mode_cartesian(mode='X')

    def test_move_tcp_pose_signature(self, easy_piper):
        """Test move_tcp_pose accepts list of 6 pose values."""
        # Should accept 6 pose values [X, Y, Z, RX, RY, RZ]
        easy_piper.move_tcp_pose([300, 0, 400, 180, 0, 0])
        easy_piper.iface.EndPoseCtrl.assert_called()
        
        # Should raise error for wrong number of values
        with pytest.raises(ValueError):
            easy_piper.move_tcp_pose([300, 0, 400])

    def test_gripper_open_close(self, easy_piper):
        """Test gripper open/close convenience methods."""
        # Test open
        easy_piper.gripper_open()
        easy_piper.iface.GripperCtrl.assert_called()
        
        # Test close
        easy_piper.gripper_close()
        easy_piper.iface.GripperCtrl.assert_called()
        
        # Test set_position
        easy_piper.gripper_set_position(50)
        easy_piper.iface.GripperCtrl.assert_called()

    def test_get_current_state_methods(self, easy_piper):
        """Test state reading methods return correct format."""
        # Test joint state
        joints = easy_piper.get_joint_state()
        assert 'j1_deg' in joints
        assert 'j6_deg' in joints
        assert 'Hz' in joints
        
        # Test TCP state
        tcp = easy_piper.get_current_tcp()
        assert 'X_mm' in tcp
        assert 'Z_mm' in tcp
        assert 'RX_deg' in tcp
        assert 'Hz' in tcp
        
        # Test gripper state
        gripper = easy_piper.get_gripper_state()
        assert 'angle_mm' in gripper
        assert 'effort_nm' in gripper
        assert 'Hz' in gripper


class TestUnitConversions:
    """Test unit conversion functions."""

    def test_degree_conversions(self):
        """Test degree to 0.001 degree conversions."""
        from easy_piper.easy_piper import _deg_to_001deg, _001deg_to_deg
        
        assert _deg_to_001deg(90.0) == 90000
        assert _deg_to_001deg(45.5) == 45500
        assert _001deg_to_deg(90000) == 90.0
        assert _001deg_to_deg(45500) == 45.5

    def test_mm_conversions(self):
        """Test millimeter to 0.001 mm conversions."""
        from easy_piper.easy_piper import _mm_to_001mm, _001mm_to_mm
        
        assert _mm_to_001mm(100.0) == 100000
        assert _mm_to_001mm(50.5) == 50500
        assert _001mm_to_mm(100000) == 100.0
        assert _001mm_to_mm(50500) == 50.5


class TestAPIConsistency:
    """Test that API is consistent across similar methods."""

    def test_method_naming_consistency(self):
        """Test that similar methods follow consistent naming patterns."""
        # All mode switching methods should start with switch_mode_
        assert hasattr(EasyPiper, 'switch_mode_joint')
        assert hasattr(EasyPiper, 'switch_mode_cartesian')
        assert hasattr(EasyPiper, 'switch_mode_move_l')
        assert hasattr(EasyPiper, 'switch_mode_move_p')
        
        # All gripper methods should start with gripper_
        assert hasattr(EasyPiper, 'gripper_enable')
        assert hasattr(EasyPiper, 'gripper_disable')
        assert hasattr(EasyPiper, 'gripper_open')
        assert hasattr(EasyPiper, 'gripper_close')
        assert hasattr(EasyPiper, 'gripper_move')
        assert hasattr(EasyPiper, 'gripper_set_position')

    def test_state_getter_consistency(self):
        """Test that state getter methods follow consistent patterns."""
        # All state getters should start with get_ and return dicts
        assert hasattr(EasyPiper, 'get_joint_state')
        assert hasattr(EasyPiper, 'get_current_tcp')
        assert hasattr(EasyPiper, 'get_gripper_state')
        assert hasattr(EasyPiper, 'get_arm_status')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
