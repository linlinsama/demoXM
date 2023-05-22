package com.example.demoXM.controller;

import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.demoXM.entity.User;
import com.example.demoXM.helper.SessionHelper;
import com.example.demoXM.service.UserService;

@Controller
public class LoginController {
	@Autowired
	private UserService UserService;


	//跳登录
	@GetMapping("/login")
	public String login() {
		return "B1A01WA01A01_登録画面";
	}

	//跳登录
	@GetMapping("/loginout")
	public String loginout(HttpSession session) {
		SessionHelper.deleteSessionRole(session);
		return "A1A01WA01A01_TOP画面";
	}

	//登陆成功返回
	@PostMapping("/top/show1")
	public String loginok(@RequestParam(name = "userid", required = false) String userid,
			@RequestParam(name = "userpsw", required = false) String userpsw, Model model, HttpSession session) {
		String role = UserService.getuserwake(userid, userpsw);
		if (role == null) {
			return "B1A01WA01A01_登録画面";
		}
		//登錄成功
		User user=new User(userid, userpsw, role);
		SessionHelper.addSessionRole(session, user);
		model.addAttribute("quanxian", role);
		return "A1A01WA01A01_TOP画面";
	}

}
