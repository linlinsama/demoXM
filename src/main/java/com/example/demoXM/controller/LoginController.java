package com.example.demoXM.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.demoXM.Service.UserService;

@Controller
public class LoginController {
	@Autowired
	private UserService UserService;
	//跳登录
	@GetMapping("/login")
	public String login() {
		return "B1A01WA01A01_登録画面";
	}
	//登陆成功返回
	@PostMapping("/top/show1")
	public String loginok(@RequestParam(name="userid",required=false)String userid,@RequestParam(name="userpsw",required=false)String userpsw,Model model) {
		System.out.println(userid+userpsw);
		String a =UserService.getuserwake(userid, userpsw);
		if(a==null) {
			return "B1A01WA01A01_登録画面";
		}
		model.addAttribute("quanxian",a);
		return "A1A01WA01A01_TOP画面";

	}



}
