extends Node3D
## ELM369 Motion Arena v0.1 — engine adapter prototype.
## QBIT-inspired values here are classical deterministic scoring, not quantum computing.

const ARENA_LIMIT := 7.0
const PLAYER_SPEED := 7.0
const TILT_DEADZONE := 0.10
const TILT_GAIN := 1.8

var player: Node3D
var camera: Camera3D
var score := 0
var lives := 3
var status_label: Label
var targets: Array[Area3D] = []
var hazards: Array[Area3D] = []
var previous_accel := Vector3.ZERO
var gyro_enabled := false

func _ready() -> void:
	_build_lighting()
	_build_floor()
	_build_player()
	_build_camera()
	_build_hud()
	_spawn_targets()
	_spawn_hazards()
	gyro_enabled = Input.get_accelerometer().length() > 0.1
	_update_hud()

func _process(delta: float) -> void:
	if lives <= 0:
		return
	var axis := _read_horizontal_axis()
	player.position.x = clampf(player.position.x + axis * PLAYER_SPEED * delta, -ARENA_LIMIT, ARENA_LIMIT)
	camera.position = camera.position.lerp(player.position + Vector3(0, 8.5, 11.5), minf(1.0, delta * 3.0))
	camera.look_at(player.position + Vector3(0, 0.5, 0), Vector3.UP)
	_check_contacts()
	_update_hud()

func _read_horizontal_axis() -> float:
	var keyboard_axis := Input.get_axis("ui_left", "ui_right")
	if absf(keyboard_axis) > 0.01:
		return keyboard_axis
	# Android accelerometer provides gravity/linear-acceleration orientation depending on device.
	# Calibrate and validate per device before treating this as production input.
	var accel := Input.get_accelerometer()
	if accel.length() < 0.1:
		return 0.0
	var tilt := accel.x
	if absf(tilt) < TILT_DEADZONE:
		return 0.0
	return clampf(tilt * TILT_GAIN, -1.0, 1.0)

func _build_lighting() -> void:
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-55, -25, 0)
	sun.light_energy = 1.4
	add_child(sun)
	var world := WorldEnvironment.new()
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.25, 0.32, 0.48)
	env.ambient_light_energy = 0.7
	world.environment = env
	add_child(world)

func _build_floor() -> void:
	var floor_body := StaticBody3D.new()
	floor_body.name = "ArenaFloor"
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(16, 0.4, 22)
	mesh.mesh = box
	mesh.position = Vector3(0, -0.35, 0)
	mesh.material_override = _material(Color(0.035, 0.09, 0.16), 0.35, 0.7)
	floor_body.add_child(mesh)
	var collider := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = box.size
	collider.shape = shape
	collider.position = mesh.position
	floor_body.add_child(collider)
	add_child(floor_body)

func _build_player() -> void:
	player = Node3D.new()
	player.name = "Player"
	var mesh := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.48
	sphere.height = 0.96
	mesh.mesh = sphere
	mesh.material_override = _material(Color(0.1, 0.85, 1.0), 0.1, 0.25)
	player.add_child(mesh)
	player.position = Vector3(0, 0.45, 6)
	add_child(player)

func _build_camera() -> void:
	camera = Camera3D.new()
	camera.name = "FollowCamera"
	camera.position = Vector3(0, 8.5, 17.5)
	camera.fov = 65.0
	add_child(camera)
	camera.look_at(Vector3.ZERO, Vector3.UP)
	camera.current = true

func _build_hud() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := PanelContainer.new()
	panel.position = Vector2(18, 18)
	panel.custom_minimum_size = Vector2(360, 100)
	layer.add_child(panel)
	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 18)
	status_label.text = "ELM369 MOTION ARENA"
	panel.add_child(status_label)

func _spawn_targets() -> void:
	for i in range(6):
		var target := _make_pickup("Target_%02d" % i, Vector3(-5.0 + float(i) * 2.0, 0.35, -3.0 - float(i % 2) * 3.0), Color(0.2, 1.0, 0.45), false)
		targets.append(target)

func _spawn_hazards() -> void:
	for i in range(3):
		var hazard := _make_pickup("Hazard_%02d" % i, Vector3(-4.0 + float(i) * 4.0, 0.45, 1.0), Color(1.0, 0.18, 0.25), true)
		hazards.append(hazard)

func _make_pickup(node_name: String, at: Vector3, tint: Color, is_hazard: bool) -> Area3D:
	var area := Area3D.new()
	area.name = node_name
	area.position = at
	var mesh := MeshInstance3D.new()
	var shape_mesh := SphereMesh.new()
	shape_mesh.radius = 0.38 if is_hazard else 0.28
	shape_mesh.height = shape_mesh.radius * 2.0
	mesh.mesh = shape_mesh
	mesh.material_override = _material(tint, 0.15, 0.25)
	area.add_child(mesh)
	var collider := CollisionShape3D.new()
	var sphere_shape := SphereShape3D.new()
	sphere_shape.radius = 0.55
	collider.shape = sphere_shape
	area.add_child(collider)
	add_child(area)
	return area

func _check_contacts() -> void:
	for target in targets.duplicate():
		if is_instance_valid(target) and player.position.distance_to(target.position) < 0.85:
			score += 10
			targets.erase(target)
			target.queue_free()
	for hazard in hazards.duplicate():
		if is_instance_valid(hazard) and player.position.distance_to(hazard.position) < 0.95:
			lives -= 1
			hazards.erase(hazard)
			hazard.queue_free()
			if lives <= 0:
				status_label.text = "GAME OVER  |  Score: %d  |  Press R to restart" % score

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_R and lives <= 0:
		get_tree().reload_current_scene()

func _update_hud() -> void:
	if is_instance_valid(status_label) and lives > 0:
		status_label.text = "ELM369 MOTION ARENA\nScore: %d   Lives: %d\nMove: ← / → or tilt phone | Avoid red hazards | Collect green targets" % [score, lives]

func _material(tint: Color, metallic_value: float, roughness_value: float) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = tint
	material.metallic = metallic_value
	material.roughness = roughness_value
	material.emission_enabled = true
	material.emission = tint * 0.22
	return material
